from rx.disposable import Disposable, CompositeDisposable, RefCountDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.internal import Struct
from rx.observable import Producer
from rx.subject import Subject
from .addRef import AddRef
import rx.linq.sink
from collections import deque
from threading import RLock


class Window(Producer):
  def __init__(self, source, count=0, skip=0, timeSpan=0, timeShift=0, scheduler=None):
    if skip == 0:
      skip = count

    self.source = source
    self.count = count # length of each window
    self.skip = skip # number of elements to skip between creation of windows
    self.timeShift = timeShift
    self.timeSpan = timeSpan
    self.scheduler = scheduler

  def run(self, observer, cancel, setSink):
    if self.scheduler == None:
      sink = self.SinkWithCount(self, observer, cancel)
      setSink(sink)
      return sink.run()
    elif self.count > 0:
      sink = self.SinkWithCountAndTimeSpan(self, observer, cancel)
      setSink(sink)
      return sink.run()
    else:
      if self.timeSpan == self.timeShift:
        sink = self.SinkWithTimeSpan(self, observer, cancel)
        setSink(sink)
        return sink.run()
      else:
        sink = self.SinkWithTimerAndTimeSpan(self, observer, cancel)
        setSink(sink)
        return sink.run()

  class SinkWithCount(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Window.SinkWithCount, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.queue = deque()
      self.n = 0
      self.m = SingleAssignmentDisposable()
      self.refCountDisposable = RefCountDisposable(self.m)

      firstWindow = self.createWindow()
      self.observer.onNext(firstWindow)

      self.m.disposable = self.parent.source.subscribeSafe(self)

      return self.refCountDisposable

    def createWindow(self):
      s = Subject()
      self.queue.append(s)
      # AddRef was originally WindowObservable but this is just an alias for AddRef
      return AddRef(s, self.refCountDisposable)

    def onNext(self, value):
      for s in self.queue:
        s.onNext(value)

      c = self.n - self.parent.count + 1

      if c >= 0 and c % self.parent.skip == 0:
        s = self.queue.popleft()
        s.onCompleted()

      self.n += 1

      if self.n % self.parent.skip == 0:
        newWindow = self.createWindow()
        self.observer.onNext(newWindow)

    def onError(self, exception):
      while len(self.queue) > 0:
        self.queue.popleft.onError(exception)

      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      while len(self.queue) > 0:
        self.queue.popleft().onCompleted()

      self.observer.onCompleted()
      self.dispose()

  class SinkWithTimeSpan(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Window.SinkWithTimeSpan, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()

      groupDisposable = CompositeDisposable()
      self.refCountDisposable = RefCountDisposable(groupDisposable)

      self.createWindow()

      groupDisposable.add(self.parent.scheduler.schedulePeriodic(self.parent.timeSpan, self.tick))
      groupDisposable.add(self.parent.source.subscribeSafe(self))

      return self.refCountDisposable

    def tick(self):
      with self.gate:
        self.subject.onCompleted()
        self.createWindow()

    def createWindow(self):
      self.subject = Subject()
      self.observer.onNext(AddRef(self.subject, self.refCountDisposable))

    def onNext(self, value):
      with self.gate:
        self.list.append(value)

    def onError(self, exception):
      with self.gate:
        self.subject.onError(exception)

        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.subject.onCompleted()

        self.observer.onCompleted()
        self.dispose()


  class SinkWithTimerAndTimeSpan(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Window.SinkWithTimerAndTimeSpan, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.totalTime = 0
      self.nextShift = self.parent.timeShift
      self.nextSpan = self.parent.timeSpan

      self.gate = RLock()
      self.queue = deque()

      self.timerDisposable = SerialDisposable()

      groupDisposable = CompositeDisposable(self.timerDisposable)
      self.refCountDisposable = RefCountDisposable(groupDisposable)

      self.createWindow()
      self.createTimer()

      groupDisposable.add(self.parent.source.subscribeSafe(self))

      return self.refCountDisposable

    def createWindow(self):
      s = Subject()
      self.queue.append(s)
      self.observer.onNext(AddRef(s, self.refCountDisposable))

    def createTimer(self):
      m = SingleAssignmentDisposable()
      self.timerDisposable.disposable = m

      isSpan = False
      isShift = False

      if self.nextSpan == self.nextShift:
        isSpan = True
        isShift = True
      elif self.nextShift < self.nextShift:
        isSpan = True
      else:
        isShift = True

      newTotalTime = self.nextSpan if isSpan else self.nextShift
      ts = newTotalTime - self.totalTime
      self.totalTime = newTotalTime

      if isSpan:
        self.nextSpan += self.parent.timeShift
      if isShift:
        self.nextShift += self.parent.timeShift

      m.disposable = self.parent.scheduler.scheduleWithRelativeAndState(
        Struct(isSpan=isSpan, isShift=isShift),
        ts,
        self.tick
      )

    def tick(self, scheduler, state):
      with self.gate:
        if state.isSpan:
          s = self.queue.popleft()
          s.onCompleted()

        if state.isShift:
          self.createWindow()

      self.createTimer()

      return Disposable.empty()

    def onNext(self, value):
      with self.gate:
        for s in self.queue:
          s.onNext(value)

    def onError(self, exception):
      with self.gate:
        for o in self.queue:
          o.onError(exception)

        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        for o in self.queue:
          o.onCompleted()

        self.observer.onCompleted()
        self.dispose()

  class SinkWithCountAndTimeSpan(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(Window.SinkWithCountAndTimeSpan, self).__init__(observer, cancel)
      self.parent = parent

    def run(self):
      self.gate = RLock()
      self.s = Subject()
      self.n = 0
      self.windowId = 0

      self.timerDisposable = SerialDisposable()
      groupDisposable = CompositeDisposable(self.timerDisposable)
      self.refCountDisposable = RefCountDisposable(groupDisposable)

      # AddRef was originally WindowObservable but this is just an alias for AddRef
      self.observer.onNext(AddRef(self.s, self.refCountDisposable))
      self.createTimer(0)

      groupDisposable.add(self.parent.source.subscribeSafe(self))

      return self.refCountDisposable

    def createTimer(self, wId):
      m = SingleAssignmentDisposable()
      self.timerDisposable.disposable = m

      m.disposable = self.parent.scheduler.scheduleWithRelativeAndState(
        wId,
        self.parent.timeSpan,
        self.tick
      )

    def tick(self, scheduler, wId):
      d = Disposable.empty()

      newId = 0

      with self.gate:
        if wId != self.windowId:
          return d

        self.n = 0
        self.windowId += 1
        newId = self.windowId

        self.s.onCompleted()
        self.s = Subject()
        self.observer.onNext(AddRef(self.s, self.refCountDisposable))

      self.createTimer(newId)

      return d

    def onNext(self, value):
      newWindow = False
      newId = 0

      with self.gate:
        self.s.onNext(value)
        self.n += 1

        if self.n == self.parent.count:
          newWindow = True
          self.n = 0
          self.windowId += 1
          newId = self.windowId

          self.s.onCompleted()
          self.s = Subject()
          self.observer.onNext(AddRef(self.s, self.refCountDisposable))

      if newWindow:
        self.createTimer(newId)

    def onError(self, exception):
      with self.gate:
        self.s.onError(exception)
        self.observer.onError(exception)
        self.dispose()

    def onCompleted(self):
      with self.gate:
        self.s.onCompleted()
        self.observer.onCompleted()
        self.dispose()