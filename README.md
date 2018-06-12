# Epip
Pipe style programming in Python



# Example
```python
# open file "data.tsv" and sum the second column
begin | "data.tsv" | open_ | map_(it | split[1]) | int_ | sum_ | end

# keep even numbers in a list
begin | [...] | filter_(it % 2 == 0) | end

# join a list using "x"
begin | [...] | str_ | join("x") | end

```

# User guide

### Coding style

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
**Functional pipe**. By adding the special pipe `it`, this nested pipe can also work as a function, which is useful when a function is desired.

#### `PIPE OPERATOR PIPE`
**Compound pipe**. When pipes are connected by operators other than "`|`", a compound pipe is created.
When data pass in, all pipes execute using the same data first, then the operations between the pipes will be executed on their outputs. For example,
```python
[1, 2, 3, 4] | sum_ / len_ # will return 2.5
```

#### Expression using `PIPE`
**Compound pipe**. When a `PIPE` is enclosed in an expression, for example `sum_+2`, the pipe will execute and then use its output for evaluating the expression.

####

### Pipe class
```python
Pipe
```

```python
List
```

```python
Iter
```

### Pipe creating functions

`as_pipe`

`side`

`switch_args`


### Special pipe objects

#### `it`

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

# More examples
See pipe.py
