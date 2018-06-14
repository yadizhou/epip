# Epip
Pipe style programming in Python

## Example
```python
# keep even numbers in a list
begin | [...] | filter_(it % 2 == 0) | end

# join a list using "x"
begin | [...] | str_ | join("x") | end

# open file "data.tsv" and sum the second column
begin | "data.tsv" | open_ | map_(it | split[1]) | int_ | sum_ | end
```

See bottom of `pipe.py` for more examples.

## Coding style

#### `[begin |] INPUT | PIPE [| PIPE...] [| end]`
**Pipe execution**. A typical command look like this. All elements are separated using "`|`".
The special pipe `begin` (in this cases optional) indicating this line is pipe style execution.
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

#### `it | PIPE [| PIPE...] [| end]`
**Functional pipe**. By adding the special pipe `it` at the beginning, this shortcut pipe can also work as a function, which is useful when a function is desired.

#### `PIPE OPERATOR PIPE`
**Compound pipe**. When pipes are connected by operators other than "`|`", a compound pipe is created.
When data pass in, all pipes execute using the same data first, then the operations between the pipes will be executed on their outputs. For example,
```python
[1, 2, 3, 4] | sum_ / len_ # will return 2.5
```

#### `PIPE` in an expression
**Compound pipe**. When a `PIPE` is enclosed in an expression, for example `sum_+2`, the pipe will execute and then use its output for evaluating the expression.
If the expression contains `it`, it can also work as a function. For example,
```python
is_even = it % 2 == 0
5 | is_even # False
is_even(4) # True
```

#### `PIPE(*args,**kwargs)`
**Arguments passing**. The associated functions of some pipes requires certain arguments, which can be passed in this way.
For example, `join("x")` creats a pipe that joins input strings with `"x"`.

## Reference
### Pipe class
#### `Pipe(FUNC)`
Turn a callable `FUNC` into a pipeable function. Base class of `List` and `Iter`.

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
list, tuple, range, dict, set, frozenset
map, zip, filter, enumerate, types.GeneratorType, reversed, type(reversed([])), type(reversed(range(0)))
```
Users can register new "need to be iterated" class by calling `Pipe.register_iterable(USER_CLASS)`

### Pipe creating functions

#### `as_pipe(ANYTHING)`

#### `side(FUNC)`

#### `switch_args(FUNC)`

### Special pipe objects

#### `it`

#### `who`

#### `begin`

#### `end`

#### `do`

#### `call`


### Flow Control

#### `If`

#### `While`


### Pre piped built-in functions

### Pre piped str methods

### Basic pipes

