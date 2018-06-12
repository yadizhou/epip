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

# Programming guide

## Pipe class
```python
Pipe
```

```python
List
```

```python
Iter
```

## Pipe creating functions
```python
as_pipe

side

switch_args
```

## Special pipe objects
```python
it
begin 
end 
do 
call 
```

## Flow Control
```python
If

While
```

## Pre piped built-in functions

## Pre piped str methods

## Basic pipes

# More examples
See pipe.py
