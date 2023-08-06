from rx.observable import Producer
import rx.linq.sink


class SkipWhile(Producer):
  def __init__(self, source, predicate, withIndex):
    self.source = source
    self.predicate = predicate
    self.withIndex = withIndex

  def run(self, observer, cancel, setSink):
    sink = self.Sink(self, observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, parent, observer, cancel):
      super(SkipWhile.Sink, self).__init__(observer, cancel)
      self.parent = parent
      self.running = False
      self.index = -1

    def onNext(self, value):
      if not self.running:
        try:
          if self.parent.withIndex:
            self.index += 1
            self.running = not self.parent.predicate(value, self.index)
          else:
            self.running = not self.parent.predicate(value)
        except Exception as e:
          self.observer.onError(e)
          self.dispose()
          return

      if self.running:
        self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()