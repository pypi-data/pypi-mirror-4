from rx.observable import Producer
import rx.linq.sink


class AsObservable(Producer):
  def __init__(self, source):
    self.source = source

  def omega(self):
    return self

  def eval(self):
    return self.source

  def run(self, observer, cancel, setSink):
    sink = self.Sink(observer, cancel)
    setSink(sink)
    return self.source.subscribeSafe(sink)

  class Sink(rx.linq.sink.Sink):
    def __init__(self, observer, cancel):
      super(AsObservable.Sink, self).__init__(observer, cancel)

    def onNext(self, value):
      self.observer.onNext(value)

    def onError(self, exception):
      self.observer.onError(exception)
      self.dispose()

    def onCompleted(self):
      self.observer.onCompleted()
      self.dispose()