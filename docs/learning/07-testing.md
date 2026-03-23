# Module 7: Testing (pytest)

> **Goal:** Understand how to write and run tests in this project.
>
> **Time:** 10 minutes
>
> **Files to open:** `tickets/tests/test_models.py`, `tickets/tests/test_services.py`, `tickets/tests/test_api.py`, `tickets/tests/factories.py`

---

## 7.1 pytest vs xUnit

| pytest | xUnit/NUnit (C#) |
|--------|-------------------|
| `def test_something(self):` | `[Fact] public void TestSomething()` |
| `assert x == y` | `Assert.Equal(y, x)` |
| `assert x is None` | `Assert.Null(x)` |
| `with pytest.raises(Error):` | `Assert.Throws<Error>(() => ...)` |
| `@pytest.mark.django_db` | (test class attribute for DB access) |
| Discovered by naming: `test_*` | Discovered by attribute: `[Fact]` |

---

## 7.2 Test Structure

```python
# tickets/tests/test_models.py
import pytest
from .factories import TicketFactory

@pytest.mark.django_db                         # REQUIRED for any test hitting the DB
class TestTicketModel:

    def test_create_ticket(self):              # method name starts with test_
        ticket = TicketFactory()               # create test data
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority is None
        assert ticket.version == 1

    def test_invalid_transition_raises(self):
        ticket = TicketFactory()
        with pytest.raises(InvalidTransitionError):   # expect this exception
            ticket.transition_to(TicketStatus.RESOLVED)
```

C# xUnit equivalent:
```csharp
public class TestTicketModel {
    [Fact]
    public void TestCreateTicket() {
        var ticket = new TicketFactory().Create();
        Assert.Equal(TicketStatus.Open, ticket.Status);
        Assert.Null(ticket.Priority);
    }

    [Fact]
    public void TestInvalidTransitionThrows() {
        var ticket = new TicketFactory().Create();
        Assert.Throws<InvalidTransitionException>(
            () => ticket.TransitionTo(TicketStatus.Resolved)
        );
    }
}
```

---

## 7.3 `@pytest.mark.django_db`

Without this decorator, pytest won't let you access the database:

```python
@pytest.mark.django_db       # YES — test can create/query models
class TestTicketModel:
    def test_create(self):
        TicketFactory()       # works

class TestWithoutDb:
    def test_create(self):
        TicketFactory()       # FAILS — database access not allowed
```

Each test runs in its own transaction that gets rolled back. Tests don't affect each other.

---

## 7.4 Factories (Test Data)

```python
# tickets/tests/factories.py
import factory
from tickets.models import Ticket

class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    subject = factory.Sequence(lambda n: f"Test Ticket {n}")   # unique per call
    body = factory.Faker("paragraph")                          # random text
    contact_email = factory.Faker("email")                     # random email
```

Usage:
```python
ticket = TicketFactory()                              # creates + saves to DB
ticket = TicketFactory(subject="Custom Subject")      # override specific fields
tickets = TicketFactory.create_batch(5)               # create 5 at once
```

C# equivalent: like Bogus + Builder pattern:
```csharp
var ticket = new Faker<Ticket>()
    .RuleFor(t => t.Subject, f => f.Lorem.Sentence())
    .Generate();
```

---

## 7.5 Three Levels of Tests

### Model tests — domain logic only

```python
def test_valid_transition(self):
    ticket = TicketFactory()
    ticket.transition_to(TicketStatus.TRIAGED)
    assert ticket.status == TicketStatus.TRIAGED
```

### Service tests — business logic with real DB

```python
def test_create_ticket(self):
    ticket = create_ticket(
        subject="Cannot login",
        body="500 error",
        contact_email="user@example.com",
    )
    assert ticket.subject == "Cannot login"
    assert ticket.status == TicketStatus.OPEN
```

### API tests — full HTTP integration

```python
def test_create_ticket(self):
    client = Client()                        # Django's test HTTP client
    response = client.post(
        "/api/tickets/",
        data={"subject": "Help", "body": "...", "contact_email": "a@b.com"},
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json()["subject"] == "Help"
```

---

## 7.6 Common Assertions

```python
assert x == y                              # equal
assert x != y                              # not equal
assert x is None                           # is null
assert x is not None                       # is not null
assert x > 0                               # greater than
assert "hello" in text                     # contains
assert len(items) == 3                     # collection length
assert isinstance(x, Ticket)              # type check

with pytest.raises(NotFoundError):         # expects exception
    get_ticket(ticket_id=uuid4())

with pytest.raises(NotFoundError, match="not found"):   # exception + message check
    get_ticket(ticket_id=uuid4())
```

---

## 7.7 Running Tests

```bash
make test          # run all tests, stop on first failure
make test-cov      # run with coverage report
```

Behind the scenes: `python -m pytest -x -v`
- `-x` — stop on first failure
- `-v` — verbose output (show test names)

---

**Next:** [Module 8: Putting It Together →](08-putting-it-together.md)
