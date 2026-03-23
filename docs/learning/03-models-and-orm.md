# Module 3: Models & ORM

> **Goal:** Define database tables and query data using Django's ORM.
>
> **Time:** 15 minutes
>
> **Files to open:** `shared/models.py`, `tickets/models.py`, `tickets/services.py`

---

## 3.1 Defining a Model

Every model inherits from `models.Model`. Fields = columns.

```python
# tickets/models.py
class Ticket(UUIDModel):
    subject = models.CharField(max_length=200)     # nvarchar(200)
    body = models.TextField()                      # nvarchar(max)
    contact_email = models.EmailField()            # nvarchar + email validation
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,               # constrains to enum values
        default=TicketStatus.OPEN,                  # default value
        db_index=True,                             # creates an index
    )
    priority = models.CharField(
        max_length=20,
        null=True,                                 # DB allows NULL
        blank=True,                                # API/forms allow empty
    )
```

C# EF equivalent:
```csharp
public class Ticket : BaseEntity {
    [MaxLength(200)]
    public string Subject { get; set; }
    public string Body { get; set; }
    public string? Priority { get; set; }   // null=True, blank=True
}
```

---

## 3.2 Field Types Cheat Sheet

| Django Field | SQL Type | C# Type |
|-------------|----------|---------|
| `CharField(max_length=N)` | `varchar(N)` | `string` |
| `TextField()` | `text` | `string` |
| `IntegerField()` | `integer` | `int` |
| `FloatField()` | `double precision` | `double` |
| `BooleanField()` | `boolean` | `bool` |
| `DateTimeField()` | `timestamp` | `DateTime` |
| `UUIDField()` | `uuid` | `Guid` |
| `EmailField()` | `varchar(254)` | `string` (with validation) |
| `ForeignKey(Model)` | `FK integer/uuid` | Navigation property |
| `OneToOneField(Model)` | `FK + unique` | One-to-one navigation |
| `ManyToManyField(Model)` | Junction table | `ICollection<T>` |

---

## 3.3 `null=True` vs `blank=True`

This trips up every beginner:

| Setting | Level | Meaning |
|---------|-------|---------|
| `null=True` | Database | Column allows NULL |
| `blank=True` | Validation | Forms/API accept empty value |

```python
# Optional field — set both
priority = models.CharField(null=True, blank=True)

# Required field — set neither (default)
subject = models.CharField(max_length=200)
```

---

## 3.4 Enums (`TextChoices`)

```python
class TicketStatus(models.TextChoices):
    OPEN = "open", "Open"                    # (db_value, display_label)
    TRIAGED = "triaged", "Triaged"
    IN_PROGRESS = "in_progress", "In Progress"
```

C# equivalent:
```csharp
public enum TicketStatus { Open, Triaged, InProgress }
// But C# enums store integers. TextChoices stores strings in the DB.
```

Usage: `choices=TicketStatus.choices` constrains the column, `TicketStatus.OPEN` gives you the value `"open"`.

---

## 3.5 `class Meta` — Model Configuration

Not a mistake — it's a class inside a class, used as a configuration container:

```python
class Ticket(UUIDModel):
    subject = models.CharField(max_length=200)

    class Meta:
        ordering = ["-created_at"]     # default ORDER BY (- = descending)
        abstract = True                # no table — inherit only
        db_table = "custom_name"       # override table name
        unique_together = ("a", "b")   # composite unique constraint
        indexes = [
            models.Index(fields=["status", "priority"]),
        ]
```

C# EF equivalent: `OnModelCreating()` configuration, but declared inline on the model.

---

## 3.6 Relationships

```python
# ForeignKey — many-to-one
class Comment(UUIDModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,        # delete comments when ticket deleted
        related_name="comments"          # enables ticket.comments.all()
    )
```

`related_name` creates a reverse navigation property:
```python
ticket.comments.all()      # get all comments for this ticket
```

C# equivalent:
```csharp
public class Ticket {
    public ICollection<Comment> Comments { get; set; }  // this is related_name
}
```

---

## 3.7 Inheritance Chain

Our models inherit through a chain:

```
models.Model              ← Django base (gives you a DB table)
    └── TimestampedModel  ← adds created_at, updated_at
            └── UUIDModel ← adds UUID primary key
                    └── Ticket, Comment, Classification, Team...
```

That's why you see `class Ticket(UUIDModel)` not `class Ticket(models.Model)` — it gets everything through the chain.

---

## 3.8 Domain Methods on Models

Models can have business logic methods:

```python
class Ticket(UUIDModel):
    def transition_to(self, new_status: str) -> None:
        allowed = VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise InvalidTransitionError("Ticket", self.status, new_status)
        self.status = new_status     # changes in MEMORY only
        self.version += 1            # changes in MEMORY only
```

**Important:** This does NOT save to the database. You must call `.save()` separately:

```python
ticket = Ticket.objects.get(id=some_id)
ticket.transition_to("triaged")    # memory only
ticket.save()                      # NOW it's persisted to DB
```

---

## 3.9 Querying Data

Every model has `.objects` — like a `DbSet<T>`:

```python
# CREATE
ticket = Ticket.objects.create(subject="Help", body="...", contact_email="a@b.com")

# READ one
ticket = Ticket.objects.get(id=ticket_id)           # throws DoesNotExist if not found

# READ many (lazy — no SQL until evaluated)
qs = Ticket.objects.filter(status="open")            # builds query
qs = qs.order_by("-created_at")                      # still no SQL
tickets = list(qs)                                   # NOW SQL executes

# UPDATE
ticket.subject = "Updated"
ticket.save()

# DELETE
ticket.delete()

# EXISTS
Ticket.objects.filter(id=ticket_id).exists()

# COUNT
Ticket.objects.filter(status="open").count()
```

---

## 3.10 Eager Loading (Avoiding N+1)

```python
# BAD — N+1 queries
tickets = Ticket.objects.all()
for t in tickets:
    print(t.comments.count())     # separate query per ticket!

# GOOD — 2 queries total
tickets = Ticket.objects.prefetch_related("comments").all()
```

| Method | SQL | Use For |
|--------|-----|---------|
| `select_related("team")` | JOIN | ForeignKey (forward) |
| `prefetch_related("comments")` | Separate IN query | Reverse FK, ManyToMany |

Both equivalent to `.Include()` in EF Core.

---

## 3.11 ORM Cheat Sheet

| Django ORM | EF Core / LINQ |
|-----------|---------------|
| `Ticket.objects.all()` | `db.Tickets` |
| `.filter(status="open")` | `.Where(t => t.Status == "open")` |
| `.exclude(status="closed")` | `.Where(t => t.Status != "closed")` |
| `.get(id=pk)` | `.First(t => t.Id == pk)` |
| `.first()` | `.FirstOrDefault()` |
| `.create(subject="x")` | `.Add(new T {...}); .SaveChanges()` |
| `.save()` | `.SaveChanges()` |
| `.delete()` | `.Remove(entity); .SaveChanges()` |
| `.exists()` | `.Any()` |
| `.count()` | `.Count()` |
| `.order_by("-created_at")` | `.OrderByDescending(t => t.CreatedAt)` |
| `.select_related("team")` | `.Include(t => t.Team)` (JOIN) |
| `.prefetch_related("comments")` | `.Include(t => t.Comments)` (separate query) |
| `.values("id", "subject")` | `.Select(t => new { t.Id, t.Subject })` |

---

## 3.12 Migrations

```bash
# After changing models:
make makemigrations     # generates migration file (like: dotnet ef migrations add)
make migrate            # applies to database (like: dotnet ef database update)
```

Django compares your current models to the last migration and auto-generates the diff. No manual SQL needed.

---

**Next:** [Module 4: Services & Business Logic →](04-services.md)
