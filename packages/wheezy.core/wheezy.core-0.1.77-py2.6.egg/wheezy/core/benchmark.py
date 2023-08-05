
""" ``bechmark`` module.
"""

from wheezy.core.comp import PY2
from wheezy.core.comp import PY_MINOR


if PY2 and PY_MINOR < 6:  # pragma: nocover
    # TODO:
    timeit = lambda f, number: 1.0
else:  # pragma: nocover
    from timeit import timeit


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

    def __init__(self, targets, number, warmup_number=None):
        """
            ``targets`` - a list of targets (callables) to be tested.

            ``number`` - how many times each target is executed.

            ``warmup_number`` - how many times each target is warmed up
            before the bechmark is measured.
        """
        self.targets = targets
        self.number = number
        self.warmup_number = warmup_number or max(int(number / 100), 10)

    def bench(self, number):
        for target in self.targets:
            yield (target.__name__, timeit(target, number=number))

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
