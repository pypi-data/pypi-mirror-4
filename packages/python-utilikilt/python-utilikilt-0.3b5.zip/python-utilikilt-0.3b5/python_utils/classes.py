import types


def MixIn(pyClass, mixInClass, makeAncestor=False):
    if makeAncestor:
        if mixInClass not in pyClass.__bases__:
            pyClass.__bases__ = (mixInClass,) + pyClass.__bases__
    else:
        # Recursively traverse the mix-in ancestor classes in order to support inheritance
        baseClasses = list(mixInClass.__bases__)
        baseClasses.reverse()
        for baseClass in baseClasses:
            MixIn(pyClass, baseClass)
        # Install the mix-in methods into the class
        for name in dir(mixInClass):
            if not name.startswith('__'):
            # skip private members
                member = getattr(mixInClass, name)
                if type(member) is types.MethodType:
                    member = member.im_func
                setattr(pyClass, name, member)


import itertools


class Indexable(object):
    """
    Takes an generator (or any iterator) and allows it to be indexable and
    slicable like naturatal lists.
    e.g.
    fib = Indexable(fibinacci())
    fib[10]  #144
    fib[5]  #13
    fib[4:10:2] #[8, 21, 55]
    """
    def __init__(self, it):
        self.it = it

    def __iter__(self):
        self.it, cpy = itertools.tee(self.it)
        return cpy

    def __getitem__(self, index):
        self.it, cpy = itertools.tee(self.it)
        if type(index) is slice:
            return list(itertools.islice(cpy, index.start, index.stop, index.step))
        else:
            return next(itertools.islice(cpy, index, index + 1))
