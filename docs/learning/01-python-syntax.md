# Module 1: Python Syntax for C# Developers

> **Goal:** Read any Python file in this project without getting confused by syntax.
>
> **Time:** 25 minutes

---

## 1.1 No Braces, Indentation Matters

```csharp
// C#
if (status == "open") {
    Console.WriteLine("open");
}
```

```python
# Python — indentation IS the block delimiter
if status == "open":
    print("open")
```

No `{}` braces, no semicolons. A colon `:` starts a block. 4 spaces of indentation defines what's inside it.

---

## 1.2 Variables and Types

```csharp
// C#
string name = "hello";
int count = 5;
List<string> items = new List<string>();
```

```python
# Python
name = "hello"                    # type is inferred
count: int = 5                    # optional type hint
items: list[str] = []             # generic syntax uses [] not <>
```

Type hints are optional and **not enforced at runtime** (like TypeScript, not like C#). They're checked by `mypy` — an external tool, not the interpreter.

---

## 1.3 Functions

```csharp
// C#
public Ticket CreateTicket(string subject, string body) {
    return new Ticket(subject, body);
}
```

```python
# Python
def create_ticket(subject: str, body: str) -> Ticket:
    return Ticket(subject=subject, body=body)
```

| C# | Python |
|----|--------|
| Access modifier + return type before name | `def` keyword, return type after `->` |
| `PascalCase` for methods | `snake_case` for everything except classes |
| `new Ticket(...)` | Just `Ticket(...)` — no `new` keyword |

---

## 1.4 Keyword-Only Arguments (`*`)

You'll see this on every service function:

```python
def create_ticket(*, subject: str, body: str, contact_email: str) -> Ticket:
```

The `*` means all arguments must be named:

```python
create_ticket("Help", "Body", "a@b.com")          # ERROR
create_ticket(subject="Help", body="Body", contact_email="a@b.com")  # OK
```

Prevents argument-order bugs. Use it whenever a function has 2+ parameters.

---

## 1.5 Imports

```csharp
// C#
using System;
using MyApp.Models;
```

```python
# Python
import uuid                              # import entire module
from uuid import UUID                    # import specific thing
from django.db import models             # from package.module import name
from .models import Ticket               # relative import (. = current package)
from shared.exceptions import NotFoundError  # absolute import
```

| Syntax | Meaning |
|--------|---------|
| `from .models` | This app's `models.py` (like `using` within same project) |
| `from ..shared` | Parent package's `shared` module |
| `from tickets.models` | Absolute path to another app |

---

## 1.6 Classes and `self`

```csharp
// C#
public class Ticket : BaseEntity {
    public string Subject { get; set; }
    public override string ToString() => $"[{Status}] {Subject}";
}
```

```python
# Python
class Ticket(UUIDModel):                   # parentheses = inheritance
    subject = models.CharField(max_length=200)

    def __str__(self) -> str:              # __str__ = ToString()
        return f"[{self.status}] {self.subject}"
```

| C# | Python |
|----|--------|
| `this` (implicit) | `self` (explicit — must be first param of every method) |
| `base()` | `super().__init__()` |
| `public` / `private` | No access modifiers. `_prefix` = convention for "private" |
| `: BaseClass` | `(BaseClass)` in parentheses |

**Dunder methods** (double underscore) are Python's magic methods:

| Python | C# Equivalent |
|--------|--------------|
| `__init__(self)` | Constructor |
| `__str__(self)` | `ToString()` |
| `__eq__(self, other)` | `Equals()` |
| `__len__(self)` | `Count` property |

---

## 1.7 Exception Handling (try/except)

```csharp
// C#
try {
    var ticket = GetTicket(id);
} catch (NotFoundException ex) {
    Console.WriteLine(ex.Message);
} catch (Exception ex) {
    Console.WriteLine($"Unexpected: {ex}");
} finally {
    Cleanup();
}
```

```python
# Python
try:
    ticket = get_ticket(id)
except NotFoundError as e:          # catch specific
    print(e.message)
except Exception as e:              # catch all
    print(f"Unexpected: {e}")
else:                               # runs ONLY if no exception (no C# equivalent)
    print("Success!")
finally:                            # always runs
    cleanup()
```

| C# | Python |
|----|--------|
| `catch (ExType ex)` | `except ExType as e` |
| `catch (A) when (...)` | No equivalent — use `if` inside `except` |
| `throw;` | `raise` (re-raise current exception) |
| `throw new Error("msg")` | `raise Error("msg")` |

---

## 1.8 The `with` Statement (like `using`)

```csharp
// C#
using (var file = File.OpenRead("data.txt")) {
    // file is auto-closed when block ends
}
```

```python
# Python
with open("data.txt") as file:
    data = file.read()
# file is auto-closed when block ends
```

Used in this project:
```python
with pytest.raises(InvalidTransitionError):    # expects an exception
    ticket.transition_to("resolved")

with transaction.atomic():                     # DB transaction block
    ticket.save()
```

---

## 1.9 Loops

```python
# for loop (like C# foreach)
for ticket in tickets:
    print(ticket.subject)

# for with index (like C# for i = 0)
for i, ticket in enumerate(tickets):
    print(f"{i}: {ticket.subject}")

# while
while not done:
    do_work()

# range (like C# Enumerable.Range)
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)
for i in range(2, 10):    # 2, 3, ..., 9
    print(i)
```

**No `do...while`** in Python. Use `while True` with `break`:
```python
while True:
    result = try_something()
    if result:
        break
```

---

## 1.10 Tuple Unpacking

```python
# Assign multiple values at once
x, y = 10, 20                     # x=10, y=20
status, count = "open", 5

# Swap without temp variable
a, b = b, a

# Unpack from function return
def get_stats():
    return 42, "ok"

count, status = get_stats()

# Ignore values with _
first, _, third = [1, 2, 3]       # _ means "don't care"
```

C# equivalent: `var (x, y) = (10, 20);` — tuple deconstruction.

---

## 1.11 Ternary / Conditional Expression

```csharp
// C#
string label = status == "open" ? "Active" : "Done";
```

```python
# Python — reads like English but backwards from C#
label = "Active" if status == "open" else "Done"
```

---

## 1.12 Lambda Functions

```csharp
// C#
Func<Ticket, string> getName = t => t.Subject;
tickets.OrderBy(t => t.CreatedAt);
```

```python
# Python
get_name = lambda t: t.subject
sorted(tickets, key=lambda t: t.created_at)
```

Lambdas in Python are limited to a single expression — no multi-line lambdas. For anything complex, use a regular `def` function.

---

## 1.13 Truthiness (Falsy Values)

In Python, many things are "falsy" — they evaluate to `False` in an `if`:

```python
# All of these are falsy:
if not None:       print("None is falsy")
if not False:      print("False is falsy")
if not 0:          print("0 is falsy")
if not "":         print("empty string is falsy")
if not []:         print("empty list is falsy")
if not {}:         print("empty dict is falsy")
```

This means you can write:
```python
# Instead of: if len(items) > 0:
if items:
    print("list has items")

# Instead of: if name != "" and name is not None:
if name:
    print("name has a value")
```

C# only has `bool` truthiness. Python's is broader — be aware of it.

---

## 1.14 `pass` — The "Do Nothing" Statement

```python
# Empty class (like {} in C#)
class MyError(Exception):
    pass                          # placeholder — body can't be empty

# Empty function
def not_implemented_yet():
    pass

# Empty if branch
if condition:
    pass    # TODO: handle this later
else:
    do_something()
```

Python requires a body for every block. `pass` is the "empty body" placeholder.

---

## 1.15 Useful Built-ins

```python
# enumerate — loop with index
for i, item in enumerate(items):
    print(f"{i}: {item}")

# zip — pair up two lists
names = ["Alice", "Bob"]
scores = [95, 87]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# any / all (like C# .Any() / .All())
has_critical = any(t.priority == "critical" for t in tickets)
all_closed = all(t.status == "closed" for t in tickets)

# sorted with key (like C# .OrderBy())
sorted_tickets = sorted(tickets, key=lambda t: t.created_at, reverse=True)

# isinstance (like C# 'is')
if isinstance(error, NotFoundError):
    handle_not_found()
```

---

## 1.16 Slicing

```python
items = [0, 1, 2, 3, 4, 5]

items[2]       # 2           — single item
items[1:4]     # [1, 2, 3]   — from index 1 up to (not including) 4
items[:3]      # [0, 1, 2]   — first 3
items[3:]      # [3, 4, 5]   — from index 3 to end
items[-1]      # 5           — last item
items[-2:]     # [4, 5]      — last 2
items[::2]     # [0, 2, 4]   — every other item

# Also works on strings
"hello"[1:3]   # "el"
```

No C# equivalent beyond `array[1..4]` range syntax (which is less flexible).

---

## 1.17 String Formatting

```python
name = "Django"

# f-string (like C# $"...")
message = f"Hello {name}, version {2 + 1}"

# Multi-line (triple quotes)
description = """
This is a
multi-line string
"""
```

---

## 1.18 None, True, False

```python
# Python        # C# equivalent
None             # null
True             # true  (capital T!)
False            # false (capital F!)
x is None        # x == null  (always use 'is' for None checks)
x is not None    # x != null
```

---

## 1.19 Collections

```python
# list = List<T>
items = [1, 2, 3]
items.append(4)                    # Add()

# dict = Dictionary<TKey, TValue>
config = {"key": "value", "count": 5}
config["key"]                      # access
config.get("missing", "default")   # safe access with fallback

# tuple = immutable group (like ValueTuple)
point = (10, 20)

# set = HashSet<T>
unique = {1, 2, 3}
```

**List comprehension** (Python's most iconic feature):
```python
names = [t.subject for t in tickets if t.status == "open"]
# C#: tickets.Where(t => t.Status == "open").Select(t => t.Subject).ToList()
```

---

## 1.20 Type Hints Reference

```python
str | None              # C#: string?  (nullable)
list[str]               # C#: List<string>
dict[str, int]          # C#: Dictionary<string, int>
UUID                    # C#: Guid
-> None                 # C#: void
```

Type hints are like TypeScript — gradually typed, checked by an external tool (`mypy`), ignored at runtime.

---

## 1.21 Decorators

Functions that wrap other functions:

```python
@router.post("/")           # like [HttpPost] attribute in C#
def create_ticket(request):
    ...

@transaction.atomic          # like a transaction wrapper
def update_ticket():
    ...

@pytest.mark.django_db       # like [DatabaseTest] attribute
def test_something():
    ...
```

You'll see decorators everywhere. Think of them as attributes + interceptors combined.

---

## 1.22 The `**` Spread Operator

```python
result = {"category": "billing", "confidence": 0.9}

# Unpack dict as keyword arguments
Classification.objects.create(ticket=ticket, **result)
# Same as: Classification.objects.create(ticket=ticket, category="billing", confidence=0.9)
```

No direct C# equivalent. `*list` unpacks a list, `**dict` unpacks a dictionary.

---

**Next:** [Module 2: Project Structure →](02-project-structure.md)
