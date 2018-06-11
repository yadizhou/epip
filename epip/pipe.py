# -*- coding: utf-8 -*-

import types
import functools


# ==================================== Core ====================================
class PipeType(type):
    def __setattr__(cls, attr, value):
        raise ValueError("This class cannot be modified.")


class Pipe(object, metaclass=PipeType):
    ITERABLE = (list, tuple, range, dict, set, frozenset)
    ITERABLE_LAZY = (map, zip, filter, enumerate, types.GeneratorType,
                     reversed, type(reversed([])), type(reversed(range(0))))
    ITERABLE_USER = []

    def __init__(self, func, name=""):
        self.func = func
        self.name = func.__name__ if not name and hasattr(func, "__name__") else name
        functools.update_wrapper(self, func)
        self.finalized = True

    # ---- Core ----
    def __or__(self, other):
        if isinstance(other, Pipe):
            return self.__class__(lambda o: self.func(o) | other)
        return NotImplemented

    def __ror__(self, other):
        return self.func(other)

    def __call__(self, *args, **kwargs):
        return self.__class__(lambda o: self.func(o, *args, **kwargs))

    def __setattr__(self, attr, value):
        if hasattr(self, "finalized"):
            raise ValueError("This object cannot be modified.")
        else:
            self.__dict__[attr] = value

    def __repr__(self):
        return "<Pipe %s>" % self.name

    @classmethod
    def register_iterable(cls, typ):
        cls.ITERABLE_USER.append(typ)

    # @formatter:off
    # ---- Comparision op ----
    def __eq__(self, other): return self.__class__(lambda o: self.func(o) == other)
    def __ne__(self, other): return self.__class__(lambda o: self.func(o) != other)
    def __lt__(self, other): return self.__class__(lambda o: self.func(o) < other)
    def __gt__(self, other): return self.__class__(lambda o: self.func(o) > other)
    def __le__(self, other): return self.__class__(lambda o: self.func(o) <= other)
    def __ge__(self, other): return self.__class__(lambda o: self.func(o) >= other)
    # ---- Arithmetic op ----
    def __neg__(self): return self.__class__(lambda o: -self.func(o))
    def __invert__(self): return self.__class__(lambda o: ~self.func(o))
    def __add__(self, other): return self.__class__(lambda o: self.func(o) + other)
    def __radd__(self, other): return self.__class__(lambda o: other + self.func(o))
    def __sub__(self, other): return self.__class__(lambda o: self.func(o) - other)
    def __rsub__(self, other): return self.__class__(lambda o: other - self.func(o))
    def __mul__(self, other): return self.__class__(lambda o: self.func(o) * other)
    def __rmul__(self, other): return self.__class__(lambda o: other * self.func(o))
    def __truediv__(self, other): return self.__class__(lambda o: self.func(o) / other)
    def __rtruediv__(self, other): return self.__class__(lambda o: other / self.func(o))
    def __floordiv__(self, other): return self.__class__(lambda o: self.func(o) // other)
    def __rfloordiv__(self, other): return self.__class__(lambda o: other // self.func(o))
    def __mod__(self, other): return self.__class__(lambda o: self.func(o) % other)
    def __rmod__(self, other): return self.__class__(lambda o: other % self.func(o))
    def __pow__(self, other): return self.__class__(lambda o: self.func(o) ** other)
    def __rpow__(self, other): return self.__class__(lambda o: other ** self.func(o))
    def __lshift__(self, other): return self.__class__(lambda o: self.func(o) << other)
    def __rlshift__(self, other): return self.__class__(lambda o: other << self.func(o))
    def __rshift__(self, other): return self.__class__(lambda o: self.func(o) >> other)
    def __rrshift__(self, other): return self.__class__(lambda o: other >> self.func(o))
    def __and__(self, other): return self.__class__(lambda o: self.func(o) & other)
    def __rand__(self, other): return self.__class__(lambda o: other & self.func(o))
    def __getitem__(self, key): return self.__class__(lambda o: self.func(o)[key])
    # @formatter:on


class List(Pipe):
    def __ror__(self, other):
        if isinstance(other, (*self.ITERABLE, *self.ITERABLE_LAZY, *self.ITERABLE_USER)):
            return [self.func(i) for i in other]
        return self.func(other)


class Iter(Pipe):
    def __ror__(self, other):
        if isinstance(other, (*self.ITERABLE, *self.ITERABLE_LAZY, *self.ITERABLE_USER)):
            return (self.func(i) for i in other)
        return self.func(other)


# Special pipes
class it(Pipe):
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class begin(Pipe):
    def __or__(self, other):
        if isinstance(other, Pipe):
            return other.func()
        return other


class end(Pipe):
    def __ror__(self, other):
        if isinstance(other, self.ITERABLE_LAZY):
            return list(other)
        return other


class do(Pipe):
    def __ror__(self, other):
        return self.func(other)

    def __call__(self, *args, **kwargs):
        return self.__class__(lambda o: o(*args, **kwargs))


class call(Pipe):
    def __ror__(self, other):
        return self.func(other)

    def __call__(self, name, *args, **kwargs):
        return self.__class__(lambda o: getattr(o, name)(*args, **kwargs))


nothing = lambda: None
passing = lambda other: other
calling = lambda o: o() if callable(o) else o
it = it(passing, name="it")
begin = begin(nothing, name="begin")
end = end(nothing, name="end")
do = do(calling, name="do")
call = call(calling, name="call")


# Pipe creation function
def as_pipe(x):
    return x if isinstance(x, Pipe) else Pipe(lambda other, r=x: r)


def side(func):
    return Pipe(lambda other, *args, **kwargs: func(other, *args, **kwargs) and 0 or other)


def switch_args(func):
    return Pipe(lambda other, first: func(first, other))


# Flow control
class FlowControl(object, metaclass=PipeType):
    def __call__(self, other):
        return other | self


class If(FlowControl):
    def __init__(self, condition, do_true, do_false=None):
        self.condition = as_pipe(condition)
        self.do_true = as_pipe(do_true)
        self.do_false = as_pipe(it if do_false is None else do_false)

    def __ror__(self, other):
        if other | self.condition | end:
            return other | self.do_true | end
        else:
            return other | self.do_false | end


class While(FlowControl):
    def __init__(self, condition, do_while, c_break=None, do_break=None):
        self.condition = as_pipe(condition)
        self.do_while = as_pipe(it if do_while is None else do_while)
        self.c_break = as_pipe(False if c_break is None else c_break)
        self.do_break = as_pipe(it if do_break is None else do_break)

    def __ror__(self, other):
        while other | self.condition | end:
            other = other | self.do_while | end
            if other | self.c_break | end:
                other = other | self.do_break | end
                break
        return other


# ================================== Builtins ==================================
# Type reducing
list_ = Pipe(list)
tuple_ = Pipe(tuple)
range_ = Pipe(range)
dict_ = Pipe(dict)
set_ = Pipe(set)

# Type non-reducing
str_ = Iter(str)
int_ = Iter(int)
bin_ = Iter(bin)
oct_ = Iter(oct)
hex_ = Iter(hex)
float_ = Iter(float)
ord_ = Iter(ord)
chr_ = Iter(chr)

# Op reducing
min_ = Pipe(min)
max_ = Pipe(max)
sum_ = Pipe(sum)
len_ = Pipe(len)

# Op non-reducing
abs_ = Iter(abs)
pow_ = Iter(pow)
round_ = Iter(round)
divmod_ = Iter(divmod)

# Truth test
bool_ = Pipe(bool)
all_ = Pipe(all)
any_ = Pipe(any)

# Iterator
map_ = switch_args(map)
zip_ = Pipe(zip)
filter_ = switch_args(filter)
sorted_ = Pipe(sorted)
reversed_ = Pipe(reversed)
enumerate_ = Pipe(enumerate)

# Attribute
setattr_ = Pipe(setattr)
getattr_ = Pipe(getattr)
hasattr_ = Pipe(hasattr)

# Meta
type_ = Pipe(type)
super_ = Pipe(super)
isinstance_ = Pipe(isinstance)
issubclass_ = Pipe(issubclass)
callable_ = Pipe(callable)
exec_ = Pipe(exec)
eval_ = Pipe(eval)

# I/O
open_ = Pipe(open)
input_ = Pipe(input)
print_ = side(print)

# unused
# frozenset_ = Pipe(frozenset)
# globals_ = Pipe(globals)
# locals_ = Pipe(locals)
# memoryview_ = Pipe(memoryview)
# delattr_ = Pipe(delattr)
# __import___ = Pipe(__import__)
# complex_ = Pipe(complex)
# dir_ = Pipe(dir)
# help_ = Pipe(help)
# id_ = Pipe(id)
# object_ = Pipe(object)
# ascii_ = Pipe(ascii)
# classmethod_ = Pipe(classmethod)
# staticmethod_ = Pipe(staticmethod)
# property_ = Pipe(property)
# vars_ = Pipe(vars)
# slice_ = Pipe(slice)
# bytearray_ = Pipe(bytearray)
# next_ = Pipe(next)
# iter_ = Pipe(iter)
# bytes_ = Pipe(bytes)
# compile_ = Pipe(compile)
# hash_ = Pipe(hash)
# format_ = Pipe(format)
# repr_ = Pipe(repr)

# =============================== Built-in Types ===============================
join = Pipe(lambda x, what: what.join(x))

split = Iter(str.split)
rsplit = Iter(str.rsplit)
splitlines = Iter(str.splitlines)
partition = Iter(str.partition)
rpartition = Iter(str.rpartition)

ljust = Iter(str.ljust)
center = Iter(str.center)
rjust = Iter(str.rjust)

lower = Iter(str.lower)
upper = Iter(str.upper)
title = Iter(str.title)
capitalize = Iter(str.capitalize)

strip = Iter(str.strip)
lstrip = Iter(str.lstrip)
rstrip = Iter(str.rstrip)

startswith = Iter(str.startswith)
endswith = Iter(str.endswith)


class str_is(object):
    alnum = Iter(str.isalnum)
    alpha = Iter(str.isalpha)
    decimal = Iter(str.isdecimal)
    digit = Iter(str.isdigit)
    lower = Iter(str.islower)
    numeric = Iter(str.isnumeric)
    space = Iter(str.isspace)
    title = Iter(str.istitle)
    upper = Iter(str.isupper)


# str.count
# str.find
# str.rfind
# str.replace

# ================================== Operator ==================================
# @formatter:off
# iter/single mode
@Iter
def add(x, y):
    return x + y
@Iter
def sub(x, y):
    return x - y
@Iter
def mul(x, y):
    return x * y
@Iter
def div(x, y):
    return x / y
@Iter
def mod(x, y):
    return x % y
@Iter
def is__(x, y):
    return x is y
@Iter
def is_not(x, y):
    return x is not y
@Iter
def in__(x, y):
    return x in y
@Iter
def not_in(x, y):
    return x not in y
# single mode
@Pipe
def add_(x, y):
    return x + y
@Pipe
def sub_(x, y):
    return x - y
@Pipe
def mul_(x, y):
    return x * y
@Pipe
def div_(x, y):
    return x / y
@Pipe
def mod_(x, y):
    return x % y
@Pipe
def is_(x, y):
    return x is y
@Pipe
def is_not_(x, y):
    return x is not y
@Pipe
def in_(x, y):
    return x in y
@Pipe
def not_in_(x, y):
    return x not in y
@Pipe
def has_(x, y):
    return y in x
@Pipe
def not_has_(x, y):
    return y not in x
@Pipe
def head(x, n=5, skip=0):
    return x[skip:skip + n]
@Pipe
def tail(x, n=5, skip=0):
    return x[-skip - n:-skip] if skip else x[-skip - n:]
# @formatter:on


# ==============================================================================
if __name__ == '__main__':
    DEBUG = False


    def T(expected, value):
        if DEBUG:
            print("." if expected == value else "X", value)
        else:
            print("." if expected == value else "X", end="")


    T(True, begin | end | is_(None))
    T(False, begin | end | is_not(None))

    # Built-ins
    T([], begin | list_ | end)
    T([1, 2], begin | (1, 2) | list_ | end)
    T(["1", "2"], begin | "12" | list_ | end)
    T((), begin | tuple_ | end)
    T((1, 2), begin | [1, 2] | tuple_ | end)
    T(("1", "2"), begin | "12" | tuple_ | end)
    T(range(4), begin | 4 | range_ | end)
    T(range(4, 8), begin | 4 | range_(8) | end)
    T(range(4, 8, 2), begin | 4 | range_(8, 2) | end)
    T({}, begin | dict_ | end)
    T({1: 2}, begin | [(1, 2)] | dict_ | end)
    T({0: 2, 1: 3}, begin | zip(range(2), range(2, 4)) | dict_ | end)
    T(set(), begin | set_ | end)
    T({1, 2}, begin | (1, 2) | set_ | end)

    T("123", begin | 123 | str_ | end)
    T(["1", "2", "3"], begin | [1, 2, 3] | str_ | end)
    T(123, begin | "123" | int_ | end)
    T([1, 2, 3], begin | ["1", "2", "3"] | int_ | end)
    T(1.5, begin | "1.5" | float_ | end)
    T([1.5, 2.5, 3.5], begin | ["1.5", "2.5", "3.5"] | float_ | end)
    T(65, begin | "A" | ord_ | end)
    T([65, 66], begin | ["A", "B"] | ord_ | end)
    T("A", begin | 65 | chr_ | end)
    T(["A", "B"], begin | [65, 66] | chr_ | end)

    T(1, begin | [1, 2, 3] | min_ | end)
    T(3, begin | [1, 2, 3] | max_ | end)
    T(6, begin | [1, 2, 3] | sum_ | end)
    T(3, begin | [1, 2, 3] | len_ | end)
    T([1, 2, 3], begin | [1, -2, 3] | abs_ | end)
    T([1, 4, 9], begin | [1, -2, 3] | pow_(2) | end)
    T([1, 2, 2], begin | [1.1, 1.5, 2.5] | round_ | end)
    T([(0, 1), (1, 0), (1, 1)], begin | [1, 2, 3] | divmod_(2) | end)

    T(False, begin | "" | bool_ | end)
    T(True, begin | [1] | bool_ | end)
    T(False, begin | [0, 1, 1] | all_ | end)
    T(True, begin | [0, 1, 1] | any_ | end)

    T(["1", "2", "3"], begin | [1, 2, 3] | map_(str) | end)
    T([(1, 3), (2, 4)], begin | [1, 2] | zip_([3, 4]) | end)
    T([2], begin | [1, 2, 3] | filter_(it % 2 == 0) | end)
    T([3, 2, 1], begin | [1, 2, 3] | sorted_(reverse=1) | end)
    T([3, 2, 1], begin | [1, 2, 3] | reversed_ | end)
    T([3, 2, 1], begin | (1, 2, 3) | reversed_ | end)
    T([(0, 1), (1, 2), (2, 3)], begin | [1, 2, 3] | enumerate_ | end)

    T(list, begin | [1, 2, 3] | type_ | end)
    T(True, begin | [1, 2, 3] | hasattr_("index") | end)
    T(1, begin | [1, 2, 3] | getattr_("index") | do(2) | end)
    T(3, begin | [1, 2, 3] | getattr_("__len__") | do | end)
    T(3, begin | [1, 2, 3] | getattr_("__len__") | call | end)
    T(1, begin | [1, 2, 3] | call("index", 2) | end)
    T([2, 3, 4], begin | [1, 2, 3] | side(it | call("__len__") | mul(1)) | add(1) | end)

    # Test
    T(True, begin | [1, 2, 3] | has_(1) | end)
    T(False, begin | [1, 2, 3] | not_has_(1) | end)
    T(True, begin | 1 | in_([1, 3]) | end)
    T([1, 0, 1], begin | [1, 2, 3] | in__([1, 3]) | end)
    T(True, begin | [1, 2, 3] | in_([[1, 2, 3], [4, 5]]) | end)
    T(False, begin | 1 | not_in([1, 3]) | end)
    T([0, 1, 0], begin | [1, 2, 3] | not_in([1, 3]) | end)
    T(False, begin | [1, 2, 3] | not_in_([[1, 2, 3], [4, 5]]) | end)

    # Flow control
    T(103, begin | [1, 2, 3] | (len_ | add(100)) | end)
    T(503, begin | [1, 2, 3] | If(sum_(5) < 90, len_ | (it + 500), -sum_) | end)
    T(0.6, begin | [1, 2, 3] | If(1, len_ | it / 5, -sum_) | end)
    T(6, begin | [1, 2, 3] | If(len_ > 2, it * 2) | len_ | end)
    T(3, begin | [1, 2, 3] | If(len_ > 4, it * 2) | len_ | end)
    T(False, begin | [1, 2, 3] | If(1, len_ | 5 / it > 5 | add(1), -sum_) | end)
    T(False, begin | [1, 2, 3] | If(1, len_ | 5 / it > (5 | add(1)), -sum_) | end)
    T(1, begin | [1, 2, 3] | If(1, len_ | (5 / it > 5) | add(1), -sum_) | end)
    T(10, begin | [1, 2, 3] | If(0, 0, sum_ | max_(10)) | end)
    T(3, begin | [1, 2, 3] | If(0, 0, max_) | end)
    T("odd", If(it % 2, "odd", "even")(3))
    T("even", If(it % 2, "odd", "even")(4))
    T([1, 2, 3, 1, 1], begin | [1, 2, 3] | While(len_ < 5, add_([1])) | end)
    T([1, 2, 3, 1, 1], begin | [1, 2, 3] | While(True, add_([1]), len_ == 5) | end)

    # Misc
    T([0, 0, 2], begin | "1,2,3" | split(",") | (int_ > 2) | mul(2) | end)
    T("1x2", begin | ["1", "2"] | join("x"))
