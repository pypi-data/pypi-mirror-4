from rx.observable import Producer
import rx.linq.sink


class Average(Producer):
  def __init__(self, source):
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, observer, cancel):
      super(Average.Sink, self).__init__(observer, cancel)
      self.sum = 0
      self.count = 0

    def onNext(self, value):
      try:
        self.sum += value
        self.count += 1
      except Exception as e:
        self.observer.onError(e)
        self.dispose()

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      try:
        self.observer.onNext(self.sum / self.count)
        self.observer.onCompleted()
      except Exception as e:
        self.observer.onError(e)
      finally:
        self.dispose()