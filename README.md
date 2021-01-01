# The Cmaj programming language

# Language design

## Basic concepts

Contrary to types, basic concepts (`None`, `Some`, `Bool`, `Int`, `Float`, `String`, and functions) are used to define
value trades. `Bool` is the closest thing to a type. This concept describes the set of the values `true` and `false`,
which are the result of boolean expressions. `Int` describes integer numbers but is not restricted to a fixed value
range. `Some` describes any concept but `None`.

## Composed concepts

Concepts can be composed as arrays, structures, and unions. The keywords `is` and `special` are used to distinguish
aliases and new concepts. `Number = Int` means that `Number` is interchangeable with `Int`. Whereas `Number < Int` means
that a `Number` can be used as an `Int`, but an `Int` cannot be used as a `Number`.

### Examples

```
IntArray = Int[]
```

```
Point < Float, Float
```

```
Optional<T> = T | None
```

## Properties

Properties are functions that take exactly one argument and return `Bool`. Properties are used to make concepts more
specific.

### Examples

```
def is_even(number Int) -> Bool
    remainder = number mod 2
    return remainder == 0
```

Properties can be the result of property factory:

```
def is_index_of(array Int[]) -> (Int) -> Bool
    def is_index(position Int) -> Bool
        return position >= 0 and position < length(array)
    return is_index
```

## Derived concepts

### Examples

Templates can be used to require consistent function definitions:

```
Sized<T> = T and defines length(T) -> Int
Sequence<T, V> = Sized<T> and defines T[Int] -> V and defines V in T
```

Concepts can be parameterized (templates can be omitted if irrelevant):

```
Index(values Sized) = Int and _ >= 0 and _ < length(values)
```

Concepts derived with `<` can be used to distinguish values. In the example below, only natural numbers that pass
the `maybe_prime` check can be used as arguments of `make_number`.

```
NaturalNumber = Int and larger_than(0)
Prime < NaturalNumber and is_prime

def maybe_prime(number NaturalNumber) -> Optional<Prime>
    if is_prime(number)
        return Prime(number)
    else
        return None

def make_number(primes Prime[]) -> NaturalNumber
    return reduce(primes, 1, _ * _)

user_input = read keyboard
def func(user_input NaturalNumber)
    my_prime = Prime(user_input)
    my_number = make_number([my_prime])
```
