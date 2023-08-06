from nose import tools

from greenrocket import Signal


def signal_test():
    signal = Signal(a=1, b=2)
    tools.eq_(signal.a, 1)
    tools.eq_(signal.b, 2)


def subscribtion_test():
    log = []

    @Signal.subscribe
    def handler(signal):
        log.append('processed: ' + repr(signal))

    Signal(value='Test').fire()
    tools.eq_(log, ["processed: Signal(value='Test')"])

    Signal.unsubscribe(handler)
    Signal(value='Test 2').fire()
    tools.eq_(log, ["processed: Signal(value='Test')"])


def double_subscribtion_test():
    log = []

    def handler(signal):
        log.append('processed: ' + repr(signal))
    Signal.subscribe(handler)
    Signal.subscribe(handler)

    Signal().fire()
    tools.eq_(log, ["processed: Signal()"])

    Signal.unsubscribe(handler)
    Signal.unsubscribe(handler)  # Should raise no error


def error_swallow_test():
    @Signal.subscribe
    def handler(signal):
        raise Exception('Test')

    Signal().fire()
    Signal.unsubscribe(handler)


def propagation_test():
    log = []

    class MySignal(Signal):
        pass

    @Signal.subscribe
    def handler(signal):
        log.append('processed by handler: ' + repr(signal))

    @MySignal.subscribe
    def my_handler(signal):
        log.append('processed by my_handler: ' + repr(signal))

    MySignal().fire()
    tools.eq_(log, ["processed by my_handler: MySignal()",
                    "processed by handler: MySignal()"])
