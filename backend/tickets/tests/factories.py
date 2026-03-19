import factory

from tickets.models import Ticket


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    subject = factory.Sequence(lambda n: f"Test Ticket {n}")
    body = factory.Faker("paragraph")
    contact_email = factory.Faker("email")
