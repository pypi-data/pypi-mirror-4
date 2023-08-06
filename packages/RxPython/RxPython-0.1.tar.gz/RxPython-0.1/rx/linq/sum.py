from rx.observable import Producer
import rx.linq.sink


class Sum(Producer):
  def __init__(self, source):
    self.source = source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, observer, cancel):
      super(Sum.Sink, self).__init__(observer, cancel)
      self.sum = 0

    def onNext(self, value):
      self.sum += value

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onNext(self.sum)
      self.observer.onCompleted()
      self.dispose()