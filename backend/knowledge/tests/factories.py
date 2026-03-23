import factory

from knowledge.models import Article


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Sequence(lambda n: f"Test Article {n}")
    content = factory.Faker("paragraph")
    category = factory.Faker("word")
    tags = factory.List([factory.Faker("word") for _ in range(3)])
    author_name = factory.Faker("name")
