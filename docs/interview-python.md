# 30 Python Interview Questions

For C# developers transitioning to Python. Each answer includes the C# equivalent where relevant.

---

## Basics

### 1. What's the difference between a list, tuple, and set?

```python
my_list = [1, 2, 3]       # mutable, ordered, allows duplicates   → List<int>
my_tuple = (1, 2, 3)      # immutable, ordered, allows duplicates  → (int, int, int) ValueTuple
my_set = {1, 2, 3}        # mutable, unordered, NO duplicates      → HashSet<int>
```

- **List** — use when you need to add/remove items. Most common.
- **Tuple** — use for fixed groups of values (like returning multiple values from a function). Immutable = can be used as dict keys.
- **Set** — use when you need uniqueness or fast `in` checks (O(1) lookup).

### 2. What's the difference between `is` and `==`?

```python
a = [1, 2, 3]
b = [1, 2, 3]

a == b    # True  — values are equal (like C# .Equals())
a is b    # False — different objects in memory (like C# Object.ReferenceEquals())

x = None
x is None  # True — always use 'is' for None checks (it's a singleton)
```

### 3. What are `*args` and `**kwargs`?

```python
def foo(*args, **kwargs):
    print(args)     # tuple of positional args: (1, 2, 3)
    print(kwargs)   # dict of keyword args: {"name": "Alice", "age": 30}

foo(1, 2, 3, name="Alice", age=30)
```

- `*args` — collects extra positional arguments into a tuple (like C# `params object[]`)
- `**kwargs` — collects extra keyword arguments into a dict (no C# equivalent)
- You can also **unpack** with them: `func(*my_list)` and `func(**my_dict)`

### 4. What are list comprehensions?

A concise way to create lists (Python's most iconic feature):

```python
# List comprehension
squares = [x**2 for x in range(10)]

# With filter
evens = [x for x in range(20) if x % 2 == 0]

# Nested
flat = [item for sublist in matrix for item in sublist]

# Dict comprehension
counts = {word: len(word) for word in words}
```

C# LINQ equivalent: `Enumerable.Range(0, 10).Select(x => x * x).ToList()`

### 5. What does `if __name__ == "__main__":` mean?

```python
def main():
    print("Running directly")

if __name__ == "__main__":
    main()
```

`__name__` is a special variable. When a file is run directly, it equals `"__main__"`. When imported as a module, it equals the module name. This prevents code from running on import — like C#'s entry point pattern but manual.

### 6. What is a decorator?

A function that wraps another function to add behavior:

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done")
        return result
    return wrapper

@log_calls                    # syntactic sugar for: greet = log_calls(greet)
def greet(name):
    return f"Hello {name}"
```

C# equivalent: like an attribute `[LogCalls]` combined with an aspect/interceptor pattern. Decorators are used everywhere in Django/Python — `@router.get()`, `@pytest.mark.django_db`, `@transaction.atomic`, `@dramatiq.actor`.

### 7. What's the difference between `@staticmethod` and `@classmethod`?

```python
class MyClass:
    count = 0

    def instance_method(self):       # receives instance as 'self'
        pass

    @classmethod
    def class_method(cls):           # receives class as 'cls'
        return cls.count             # like static method that knows its class

    @staticmethod
    def static_method():             # receives nothing — pure function
        pass                         # like C# static method
```

- `@classmethod` — useful for alternative constructors: `Ticket.from_email(raw_email)`
- `@staticmethod` — rarely used in practice, just a function that lives on a class

### 8. How does Python handle memory management?

- **Reference counting** — each object tracks how many references point to it. When count hits 0, memory is freed immediately.
- **Garbage collector** — handles circular references that reference counting can't detect.
- No manual memory management (like C#'s GC, but simpler — no `IDisposable`).
- `del x` removes a reference, doesn't force deletion.

### 9. What are generators?

Functions that `yield` values lazily instead of returning a list:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a           # pauses here, resumes on next iteration
        a, b = b, a + b

for n in fibonacci():
    if n > 100:
        break
    print(n)
```

C# equivalent: `IEnumerable<T>` with `yield return`. Same concept, same keyword.

Generator expressions (like lazy list comprehensions):
```python
sum(x**2 for x in range(1000000))   # doesn't create a list in memory
```

### 10. What is the GIL (Global Interpreter Lock)?

The GIL is a mutex that allows only one thread to execute Python bytecode at a time. This means:

- **CPU-bound** work doesn't benefit from threading (use `multiprocessing` instead)
- **I/O-bound** work (network, disk) still benefits from threading (the GIL is released during I/O)
- `asyncio` is the preferred approach for I/O-bound concurrency

C# has no GIL — `Task.Run()` uses real OS threads. In Python, true parallelism requires multiple processes.

---

## Intermediate

### 11. Mutable default arguments — what's the bug?

```python
# BUG: the list is shared across ALL calls!
def append_to(item, target=[]):
    target.append(item)
    return target

append_to(1)  # [1]
append_to(2)  # [1, 2] — NOT [2]!

# FIX: use None as default
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

Default arguments are evaluated ONCE when the function is defined, not on each call. Mutable defaults (list, dict, set) are shared across calls. This is the #1 Python gotcha.

### 12. What's the difference between shallow copy and deep copy?

```python
import copy

original = [[1, 2], [3, 4]]

shallow = original.copy()           # or list(original) or original[:]
shallow[0].append(5)
print(original)  # [[1, 2, 5], [3, 4]] — inner lists are shared!

deep = copy.deepcopy(original)
deep[0].append(6)
print(original)  # [[1, 2, 5], [3, 4]] — fully independent
```

### 13. What are context managers (`with` statement)?

```python
with open("file.txt") as f:     # __enter__ is called
    data = f.read()
# __exit__ is called automatically (even on exception)
```

C# equivalent: `using` statement with `IDisposable`. You can create custom ones:

```python
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield                        # code inside 'with' block runs here
    print(f"Took {time.time() - start:.2f}s")

with timer():
    do_work()
```

### 14. Explain Python's exception handling

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:      # catch specific (like C# catch)
    print(f"Error: {e}")
except (TypeError, ValueError):     # catch multiple types
    print("Type or value error")
except Exception as e:              # catch all (like C# catch(Exception))
    print(f"Unexpected: {e}")
else:                               # runs if NO exception (no C# equivalent)
    print("Success!")
finally:                            # always runs (like C# finally)
    cleanup()
```

The `else` clause is unique to Python — it runs only when the `try` block succeeds without exceptions.

### 15. What are dataclasses?

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"    # default value
```

Auto-generates `__init__`, `__repr__`, `__eq__`. C# equivalent: `record Point(double X, double Y, string Label = "origin");`

In this project we use Pydantic `Schema` instead (which is like dataclass + validation).

### 16. What is duck typing?

"If it walks like a duck and quacks like a duck, it's a duck."

```python
def get_length(thing):
    return len(thing)       # works with str, list, dict, any object with __len__

get_length("hello")         # 5
get_length([1, 2, 3])       # 3
get_length({"a": 1})        # 1
```

No interface required. If the object has the right methods, it works. This is why Python doesn't need DI interfaces — you just pass any object that has the right methods.

C# equivalent: imagine if every method parameter was `dynamic` — but with type hints for documentation.

### 17. What are `property` decorators?

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):                     # accessed like an attribute: circle.area
        return 3.14 * self._radius ** 2

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
```

C# equivalent: properties with `get` and `set` accessors. Exact same concept.

### 18. How does Python's import system work?

```python
import os                          # import module
from os import path                # import specific name
from os.path import join           # import nested name
from . import models               # relative import (current package)
from ..shared import exceptions    # relative import (parent package)
import json as j                   # alias (like C# using alias)
```

- Python searches: current directory → `PYTHONPATH` → installed packages → stdlib
- Each `.py` file is a module. Each directory with `__init__.py` is a package.
- Modules are cached after first import (singleton behavior)
- Circular imports are a real issue — solve with lazy imports inside functions

### 19. What is `__init__.py`?

A file that marks a directory as a Python package (importable). Can be empty or contain initialization code.

```
tickets/
├── __init__.py          # makes 'tickets' a package
├── models.py            # import: from tickets.models import Ticket
└── services.py          # import: from tickets.services import create_ticket
```

In modern Python (3.3+), `__init__.py` is technically optional for "namespace packages," but Django requires it.

### 20. Explain `enumerate`, `zip`, and common built-ins

```python
# enumerate — loop with index (like C# .Select((item, i) => ...))
for i, ticket in enumerate(tickets):
    print(f"{i}: {ticket.subject}")

# zip — pair up two lists (like C# .Zip())
names = ["Alice", "Bob"]
scores = [95, 87]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# any/all — like C# .Any() / .All()
has_critical = any(t.priority == "critical" for t in tickets)
all_closed = all(t.status == "closed" for t in tickets)

# sorted with key — like C# .OrderBy()
sorted_tickets = sorted(tickets, key=lambda t: t.created_at, reverse=True)

# map/filter — like C# .Select() / .Where() (but prefer comprehensions)
names = list(map(lambda t: t.subject, tickets))
```

---

## Advanced

### 21. What are type hints and how are they enforced?

```python
def greet(name: str, times: int = 1) -> str:
    return (name + " ") * times

x: list[dict[str, int]] = [{"age": 30}]
y: str | None = None               # Union type (Python 3.10+)
```

Type hints are **NOT enforced at runtime** — Python ignores them. They're for:
- `mypy` static analysis (like TypeScript's compiler)
- IDE autocomplete
- Documentation

This is the #1 surprise for C# developers. Python runs `greet(123)` without error even though the hint says `str`.

### 22. What are `__slots__`?

```python
class Point:
    __slots__ = ("x", "y")     # restricts attributes, saves memory

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 3    # AttributeError! — can't add attributes not in __slots__
```

Saves ~40% memory per instance by avoiding the per-instance `__dict__`. Used in performance-critical code with millions of instances.

### 23. What is a metaclass?

A class whose instances are themselves classes. `type` is the default metaclass.

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # modify or validate the class before it's created
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

class MyClass(metaclass=Meta):
    pass
```

Django uses metaclasses heavily — `models.Model` uses a metaclass that reads your field definitions and builds the ORM mapping. You rarely write metaclasses yourself, but understanding they exist helps you understand Django's "magic."

### 24. What is `asyncio`?

```python
import asyncio

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    results = await asyncio.gather(
        fetch_data("https://api.example.com/a"),
        fetch_data("https://api.example.com/b"),
    )
```

C# equivalent: `async/await` with `Task`. Very similar syntax. The key difference: Python's asyncio is single-threaded (event loop), while C#'s is multi-threaded (thread pool).

Django is traditionally synchronous. Async views exist but are not widely used yet. This project uses Dramatiq (separate worker process) instead of async.

### 25. What are magic methods (dunder methods)?

| Python | C# | Purpose |
|--------|-----|---------|
| `__init__(self)` | Constructor | Initialize instance |
| `__str__(self)` | `ToString()` | Human-readable string |
| `__repr__(self)` | (debug display) | Developer-readable string |
| `__eq__(self, other)` | `Equals()` | Equality comparison |
| `__hash__(self)` | `GetHashCode()` | Hash for dict/set |
| `__len__(self)` | `Count` property | `len(obj)` |
| `__getitem__(self, key)` | `this[key]` | `obj[key]` indexer |
| `__iter__(self)` | `GetEnumerator()` | Make iterable |
| `__enter__`/`__exit__` | `IDisposable` | Context manager |
| `__call__(self)` | (no equivalent) | Make instance callable like a function |

### 26. How does method resolution order (MRO) work?

```python
class A:
    def greet(self): return "A"

class B(A):
    def greet(self): return "B"

class C(A):
    def greet(self): return "C"

class D(B, C):     # multiple inheritance!
    pass

D().greet()        # "B" — Python uses C3 linearization
print(D.__mro__)   # (D, B, C, A, object)
```

Python supports multiple inheritance (C# doesn't — only interfaces). MRO determines the order methods are searched. Django uses this for mixins.

### 27. What are descriptors?

Objects that define `__get__`, `__set__`, or `__delete__`. Django model fields ARE descriptors:

```python
class CharField:
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if len(value) > self.max_length:
            raise ValueError("Too long")
        obj.__dict__[self.name] = value
```

When you write `ticket.subject = "Help"`, Python calls `CharField.__set__()`. This is how Django fields do validation and type conversion transparently.

### 28. What is monkey patching?

Modifying classes or modules at runtime:

```python
# In tests — replace a function temporarily
from unittest.mock import patch

@patch("triage.services.call_llm")
def test_classify(mock_llm):
    mock_llm.return_value = {"category": "billing"}
    result = classify_ticket(ticket_id=some_id)
    assert result.category == "billing"
```

This is how Python does test mocking without DI interfaces. `@patch` temporarily replaces a function and restores it after the test. C# equivalent: using a mocking framework like Moq, but without needing interfaces.

### 29. What is the walrus operator (`:=`)?

Assignment inside expressions (Python 3.8+):

```python
# Without walrus
results = fetch_results()
if results:
    process(results)

# With walrus — assign and check in one line
if results := fetch_results():
    process(results)

# Useful in loops
while chunk := file.read(8192):
    process(chunk)
```

### 30. What's the difference between `__new__` and `__init__`?

```python
class Singleton:
    _instance = None

    def __new__(cls):              # creates the instance (called BEFORE __init__)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):            # initializes the instance (called AFTER __new__)
        self.value = 42
```

- `__new__` — allocates memory, creates the object (rarely overridden)
- `__init__` — initializes the object (your "constructor")

C# has no equivalent of `__new__` — the CLR handles allocation. You'd only override `__new__` for singletons, caching, or immutable types.
