
""" ``bechmark`` module.
"""

from wheezy.core.comp import PY2
from wheezy.core.comp import PY_MINOR


if PY2 and PY_MINOR < 6:  # pragma: nocover
    import gc
    from itertools import repeat
    from time import time as default_timer

    def timeit(f, number=1000000):
        it = repeat(None, number)
        e = gc.isenabled()
        gc.disable()
        try:
            t0 = default_timer()
            for i in it:
                f()
            t1 = default_timer()
            return t1 - t0
        finally:
            if e:
                gc.enable()

else:  # pragma: nocover
    from timeit import timeit
    from timeit import default_timer  # noqa


class Benchmark(object):
    """ Measure execution time of your code.

        >>> def test_1():
        ...     pass
        >>> def test_2():
        ...     pass
        >>> b = Benchmark((test_1, test_2), 1000)
        >>> b.report() # doctest: +ELLIPSIS
        noname: 2 x 1000
        baseline throughput change target
          100.0% ...rps  +0.0% test_1
        ...% ...rps ...% test_2
    """

    def __init__(self, targets, number, warmup_number=None, timer=None):
        """
            ``targets`` - a list of targets (callables) to be tested.

            ``number`` - how many times each target is executed.

            ``warmup_number`` - how many times each target is warmed up
            before the bechmark is measured.
        """
        self.targets = targets
        self.number = number
        self.warmup_number = warmup_number or max(int(number / 100), 10)
        if timer is not None:
            self.timer = timer
            self.bench = self.bench_timer

    def bench(self, number):
        for target in self.targets:
            yield (target.__name__, timeit(target, number=number))

    def bench_timer(self, number):
        for target in self.targets:
            self.timer.start()
            timeit(target, number=number)
            self.timer.stop()
            yield (target.__name__, self.timer.timing)

    def run(self):
        # warm up
        list(self.bench(self.warmup_number))
        # run
        return self.bench(self.number)

    def report(self, name=None, baselines=None):
        baselines = baselines or {}
        print("%s: %s x %s" % (name or 'noname',
                               len(self.targets), self.number))
        print("%s %s %s %s" % ("baseline", "throughput", "change", "target"))
        base = None
        for (name, result) in self.run():
            if base is None:
                base = result
            base_relative = round(base / result, 3)
            rps = round(self.number / result, 1)
            previous_relative = baselines.get(name, base_relative)
            delta = base_relative / previous_relative - 1.0
            print("%7.1f%% %7drps %+5.1f%% %s" % (
                base_relative * 100, rps, delta * 100, name))


class Timer(object):
    """ Intercept a call to given method in order to compute
        timing.

        >>> class A(object):
        ...     def test(self):
        ...         pass
        >>> a = A()
        >>> def test():
        ...     a.test()
        >>> b = Benchmark((test, ), 1000, timer=Timer(a, 'test'))
        >>> b.report() # doctest: +ELLIPSIS
        noname: 1 x 1000
        baseline throughput change target
          100.0% ...rps  +0.0% test
    """

    def __init__(self, target, name):
        assert hasattr(target, name)
        assert callable(getattr(target, name))
        self.target = target
        self.name = name

    def start(self):
        self.timing = 0.0
        self.saved = saved = getattr(self.target, self.name)

        def timing_wrapper(*args, **kwargs):
            t0 = default_timer()
            result = saved(*args, **kwargs)
            t1 = default_timer()
            self.timing += t1 - t0
            return result
        setattr(self.target, self.name, timing_wrapper)

    def stop(self):
        setattr(self.target, self.name, self.saved)
