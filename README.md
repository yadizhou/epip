# Epip

[![PyPI version](https://badge.fury.io/py/Epip.svg)](https://badge.fury.io/py/Epip)
[![Python35](https://img.shields.io/badge/python-3.5-blue.svg)](https://badge.fury.io/py/Epip)
[![Python36](https://img.shields.io/badge/python-3.6-blue.svg)](https://badge.fury.io/py/Epip)

Pipe/Symbolic style programming in Python. The best way to understand what this package provides is to see some examples below.

To install, `pip install epip`

Then import specific members (see reference), or just `from epip import *`. No built-ins will be shadowed.

## Example
Here are some simple examples. You can also find nearly 100 examples at the end of `pipe.py`. There are also examples later in this document.
```python
# keep even numbers in a list
begin | [...] | filter_(it % 2 == 0) | end

# join a list using "x"
begin | [...] | str_ | join("x") | end

# several ways to open text file "data.tsv" -> split each line - >
#   convert the second column to int -> and sum them
begin | "data.tsv" | open_ | map_(it | split[1]) | int_ | sum_ | end
begin | "data.tsv" | open_ | each | split[1] | int_ | sum_ | end
begin | "data.tsv" | open_ | each.split()[1] | int_ | sum_ | end

# symbolic execution for calculating the average of 0-9
begin | range(10) | sum_ / len_ | end
```

## Coding style

#### `[begin |] INPUT | PIPE [| PIPE...] [| end]`
**Pipe execution**. A typical command looks like this. All elements are separated using "`|`".
The special pipe `begin` (in this cases optional and only for better readability) indicating this line is pipe style execution.
Then an input, for example, a `list`, is followed. A `PIPE` takes the input on its left as the first argument,
and call its associated function. The returned output is used as input for the next `PIPE`.
The special pipe `end` marks the end of the current pipe, which is optional is some cases.

#### `begin | PIPE [| PIPE...] [| end]`
**Pipe execution**. When there is no input, the associated function of the first `PIPE` will be called with no arguments to generate an output.

#### `PIPE [| PIPE...] [| end]`
**Shortcut pipe**. Generates a pipe shortcut, which works as if the original pipes are executed.
In this case you can assign a name for it and use it later. For example,
```python
tsv2dic = open_ | map_(it | rstrip("\n") | split(maxsplit=1)) | dict_
data = "filename.tsv" | tsv2dic
```
The special pipes `it` and `who` are used to reference the input directly. Their difference is discussed below.

#### `it | PIPE [| PIPE...] [| end]`
**Functional/shortcut pipe**. If `it` is at the beginning, this shortcut pipe can also work as a function, which is useful when a function is desired.

#### `PIPE(*args,**kwargs)`
**Arguments passing**. The associated functions of some pipes requires certain argument(s), which can be passed in this way.
For example, `join("x")` creates a pipe that joins input strings with `"x"`.

#### `PIPE` in an expression
When a `PIPE` is enclosed in an expression, for example `sum_ + 2`, the pipe will execute and then use its output for the evaluation of the expression.
If the expression contains `it`, it can also work as a function. For example,
```python
is_even = it % 2 == 0
5 | is_even # False
is_even(4) # True
```
When data pass in, all pipes in the same expression execute using the same (as long as the pipe doesn't change the input) input first, then the operations between the pipes will be executed on their outputs. For example,
```python
[1, 2, 3, 4] | sum_ / len_ # will return 2.5
```
If a pipe is used as an argument for another pipe, the pipe will be executed first when data pass in, then the outside pipe will execute.
Pipes need to know whether argument is a pipe (which should be executed first to get the output), or anything else. In this case, use the
special pipes `it` and `who` at the beginning to distinguish. `it` indicates it's a function, while `who` means it's a pipe shortcut.
```python
"1234" | split(who[2]) # ['12', '4']
"1234" | filter_(it!="3") | end # ['1', '2', '4']
```
In the two examples above, `it` and `who` are not interchangeable, since `filter_` requires a function, while `split` requires a value,
which is generated when the pipe `who[2]` is evaluated. The unrolled version of the first example is `"1234" | split("1234" | who[2])`.

Note that not all expressions are supported. For example `[PIPE1, PIPE2]` will not execute `PIPE1` and `PIPE2` then use their outputs to generate the list.
Whether a pipe expression work as expected depends on the execution order of Python. Only a `PIPE` knows how to handle other pipes, and `[ ]` is not a `PIPE`.
This limitation can be solved with a helper pipe, though.

#### `PIPE.ATTR`
**Attribute access**. A quick way to access the attribute `ATTR` of the output from `PIPE`. For example,
```python
fibo = who.append(who[-2:] | sum_)  # Append the next Fibonacci number
x = [1, 1]
for i in range(10):
    x | fibo
print(x)  # [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
```
Note that magic functions cannot be accessed in this way. They can, however, be accessed using `getattr_` or `call` (if the attribute is callable and you want to call it).

## Reference
### Pipe classes
These classes are used to create pipes. Simply instantiate them by passing them the actual functions for the pipes.

#### `Pipe(FUNC)`
Turn a callable `FUNC` into a pipeable function. Base class of `List` and `Iter` and all other pipes. All pipes are non-modifiable.

#### `List(FUNC)`
Turn a callable `FUNC` into a pipeable function, which will be applied to each element from the input if the input is an "need to be iterated" object (see below),
to generate a list containing the results. `FUNC` will be evaluated when the `List` type pipe is executed.
If the input is not a "need to be iterated" object, `List` works as a regular `Pipe`.

#### `Iter(FUNC)`
Turn a callable `FUNC` into a pipeable function, which will be applied to each element from the input if the input is an "need to be iterated" object (see below),
to generate a generator that yeilds the results. `FUNC` will **not** be evaluated when the `Iter` type pipe is executed, unless it's told to do so by the special pipe `end`.
If the input is not a "need to be iterated" object, `Iter` works as a regular `Pipe`.

"need to be iterated" classes includes:
```python
# The following does not require an "end"
list, tuple, range, dict, set, frozenset
# The following require an "end" explicitly if the actuall value is required for the next pipe
map, zip, filter, enumerate, types.GeneratorType, reversed, type(reversed([])), type(reversed(range(0)))
```
Users can register new "need to be iterated" class by calling `Pipe.register_iterable(USER_CLASS)`

### Pipe creating functions
These functions can also be used to create pipes. They add an extra layer of wrapper between the actual functions and the pipe classes, to alter the usage of the functions.

#### `as_pipe(ANYTHING)`
Turns `ANYTHING` into a pipe, which returns `ANYTHING` when executed. Useful for producing constants.

#### `side(FUNC)`
Turns a function `FUNC` into a pipe when being executed, produces some side effect (e.g., print something), then return the input.

#### `switch_args(FUNC)`
Turns a function `FUNC` into a pipe that will use the input as its second argument, while the first argument being the one directly passed to the pipe.

### Special pipe objects
The following pipes are unique pipes that serve for special cases.

#### `it`
Reference to the input itself. When used as the first pipe of a pipe shortcut, it turns the shortcut into a pipe that can also be called like a function.
`it` can be used as a simpler way to define a lambda function, e.g., `sorted([("a", 2), ("b", 1), ("c", 3)], key=it[1])`

#### `who`
Reference to the input itself.

#### `each`
Iter through each element of the input. E.g., `"123" | each * 2 | end  # ['11', '22', '33']`

#### `begin`
Return the output from the pipe on its right (by calling that pipe's function with no args), or return whatever is on its right.

#### `end`
If the input type is in any of the lazy iteratable `map, zip, filter, enumerate, types.GeneratorType, reversed, type(reversed([])), type(reversed(range(0)))`,
executes the input to get the actual output. Required if the output is needed.

#### `do`
If the input if callable, call the input with arguments passed to `do`.
```python
begin | [1, 2, 3] | getattr_("__len__") | do | end  # 3
```

#### `call`
Similar to `do`, but requires a first argument which is the string name of the callable attribute of the input.
```python
begin | [1, 2, 3] | call("index", 2) | end  # 1
```

### Flow Control
These classes are for creating complex pipes that need to have certain flow control abilities. They take pipes as arguments for instantiation.
In addition, the flow control pipes created by `If` and `While` can also be used as a function, just like `it`.

#### `If(CONDITION, DO_TRUE, DO_FALSE=None)`
If `input | CONDITION` is `True`, execute `input | DO_TRUE`, otherwise execute `input | DO_FALSE`. `DO_FALSE` is optional.
By default the input is returned as the output if `DO_FALSE` is omitted and `input | CONDITION` is `False`.

#### `While(CONDITION, DO_WHILE, C_BREAK=None, DO_BREAK=None)`
While `input | CONDITION` is `True`, update `input = input | DO_WHILE`, then check if `input | C_BREAK`.
If the break condition is met, update `input = input | DO_BREAK` then exit the loop.

### Pre piped built-in functions
Pipes have been create for the following Python built-in functions:

| Pipe name     | built-in function  | Pipe type     |
| ------------- | ------------------ | ------------- |
| `list_` | `list` | `Pipe` |
| `tuple_` | `tuple` | `Pipe` |
| `range_` | `range` | `Pipe` |
| `dict_` | `dict` | `Pipe` |
| `set_` | `set` | `Pipe` |
| `str_` | `str` | `Iter` |
| `int_` | `int` | `Iter` |
| `bin_` | `bin` | `Iter` |
| `oct_` | `oct` | `Iter` |
| `hex_` | `hex` | `Iter` |
| `float_` | `float` | `Iter` |
| `ord_` | `ord` | `Iter` |
| `chr_` | `chr` | `Iter` |
| `min_` | `min` | `Pipe` |
| `max_` | `max` | `Pipe` |
| `sum_` | `sum` | `Pipe` |
| `len_` | `len` | `Pipe` |
| `abs_` | `abs` | `Iter` |
| `pow_` | `pow` | `Iter` |
| `round_` | `round` | `Iter` |
| `divmod_` | `divmod` | `Iter` |
| `bool_` | `bool` | `Pipe` |
| `all_` | `all` | `Pipe` |
| `any_` | `any` | `Pipe` |
| `map_` | `map` | `switch_args` |
| `zip_` | `zip` | `Pipe` |
| `filter_` | `filter` | `switch_args` |
| `sorted_` | `sorted` | `Pipe` |
| `reversed_` | `reversed` | `Pipe` |
| `enumerate_` | `enumerate` | `Pipe` |
| `setattr_` | `setattr` | `Pipe` |
| `getattr_` | `getattr` | `Pipe` |
| `hasattr_` | `hasattr` | `Pipe` |
| `type_` | `type` | `Pipe` |
| `super_` | `super` | `Pipe` |
| `isinstance_` | `isinstance` | `Pipe` |
| `issubclass_` | `issubclass` | `Pipe` |
| `callable_` | `callable` | `Pipe` |
| `exec_` | `exec` | `Pipe` |
| `eval_` | `eval` | `Pipe` |
| `open_` | `open` | `Pipe` |
| `input_` | `input` | `Pipe` |
| `print_` | `print` | `side` |

### Pre piped str methods
Pipes have been create for the following Python `str` methods:

| Pipe name     | str function       | Pipe type     |
| ------------- | ------------------ | ------------- |
| `join` | `other_str.join` | `Pipe` |
| `format_` | `other_str.format` | `Iter` |
| `split` | `str.split` | `Iter` |
| `rsplit` | `str.rsplit` | `Iter` |
| `splitlines` | `str.splitlines` | `Iter` |
| `partition` | `str.partition` | `Iter` |
| `rpartition` | `str.rpartition` | `Iter` |
| `ljust` | `str.ljust` | `Iter` |
| `center` | `str.center` | `Iter` |
| `rjust` | `str.rjust` | `Iter` |
| `lower` | `str.lower` | `Iter` |
| `upper` | `str.upper` | `Iter` |
| `title` | `str.title` | `Iter` |
| `capitalize` | `str.capitalize` | `Iter` |
| `strip` | `str.strip` | `Iter` |
| `lstrip` | `str.lstrip` | `Iter` |
| `rstrip` | `str.rstrip` | `Iter` |
| `startswith` | `str.startswith` | `Iter` |
| `endswith` | `str.endswith` | `Iter` |
| `str_is.alnum` | `str.isalnum` | `Iter` |
| `str_is.alpha` | `str.isalpha` | `Iter` |
| `str_is.decimal` | `str.isdecimal` | `Iter` |
| `str_is.digit` | `str.isdigit` | `Iter` |
| `str_is.lower` | `str.islower` | `Iter` |
| `str_is.numeric` | `str.isnumeric` | `Iter` |
| `str_is.space` | `str.isspace` | `Iter` |
| `str_is.title` | `str.istitle` | `Iter` |
| `str_is.upper` | `str.isupper` | `Iter` |

### Basic pipes
| `Iter`        | `Pipe`        |
| ------------- | ------------- |
| `add` | `add_` |
| `sub` | `sub_` |
| `mul` | `mul_` |
| `div` | `div_` |
| `mod` | `mod_` |
| `is__` | `is_` |
| `is_not` | `is_not_` |
| `in__` | `in_` |
| `not_in` | `not_in_` |
|  | `has_` |
|  | `not_has_` |
|  | `head` |
|  | `tail` |