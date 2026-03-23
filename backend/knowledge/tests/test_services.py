import uuid

import dramatiq
import pytest

from shared.exceptions import InvalidTransitionError, NotFoundError
from knowledge.services import (
    create_article,
    delete_article,
    generate_tags,
    get_article,
    list_articles,
    transition_article,
    update_article,
)

from .factories import ArticleFactory


@pytest.mark.django_db
class TestCreateArticle:
    def test_create_article(self):
        article = create_article(
            title="Login Guide",
            content="How to login to the dashboard.",
            category="authentication",
            tags=["login", "auth"],
            author_name="John Doe",
        )
        assert article.title == "Login Guide"
        assert article.content == "How to login to the dashboard."
        assert article.category == "authentication"
        assert article.tags == ["login", "auth"]
        assert article.author_name == "John Doe"
        assert article.status == "draft"

    def test_create_article_with_empty_tags(self):
        article = create_article(
            title="Test",
            content="Body",
            category="general",
            tags=[],
            author_name="Jane",
        )
        assert article.tags == []


@pytest.mark.django_db
class TestGetArticle:
    def test_get_existing_article(self):
        created = ArticleFactory(title="Find Me")
        found = get_article(article_id=created.id)
        assert found.id == created.id
        assert found.title == "Find Me"

    def test_get_nonexistent_article(self):
        with pytest.raises(NotFoundError):
            get_article(article_id=uuid.uuid4())


@pytest.mark.django_db
class TestListArticles:
    def test_list_all(self):
        ArticleFactory.create_batch(3)
        articles = list_articles()
        assert len(articles) == 3

    def test_list_empty(self):
        articles = list_articles()
        assert articles == []

    def test_list_filter_by_category(self):
        ArticleFactory(category="auth")
        ArticleFactory(category="auth")
        ArticleFactory(category="billing")
        articles = list_articles(category="auth")
        assert len(articles) == 2
        assert all(a.category == "auth" for a in articles)

    def test_list_filter_no_match(self):
        ArticleFactory(category="auth")
        articles = list_articles(category="billing")
        assert articles == []


@pytest.mark.django_db
class TestUpdateArticle:
    def test_update_article(self):
        article = ArticleFactory(title="Old Title", category="general")
        updated = update_article(
            article_id=article.id,
            title="New Title",
            content="New content",
            category="updated",
            tags=["new"],
        )
        assert updated.title == "New Title"
        assert updated.content == "New content"
        assert updated.category == "updated"
        assert updated.tags == ["new"]

    def test_update_nonexistent_article(self):
        with pytest.raises(NotFoundError):
            update_article(
                article_id=uuid.uuid4(),
                title="X",
                content="X",
                category="X",
                tags=[],
            )


@pytest.mark.django_db
class TestDeleteArticle:
    def test_delete_article(self):
        article = ArticleFactory()
        delete_article(article_id=article.id)
        with pytest.raises(NotFoundError):
            get_article(article_id=article.id)

    def test_delete_nonexistent_article(self):
        with pytest.raises(NotFoundError):
            delete_article(article_id=uuid.uuid4())


@pytest.mark.django_db
class TestTransitionArticle:
    def test_transition_draft_to_published(self):
        article = ArticleFactory(status="draft")
        result = transition_article(article_id=article.id, new_status="published")
        assert result.status == "published"

    def test_transition_invalid(self):
        article = ArticleFactory(status="draft")
        with pytest.raises(InvalidTransitionError):
            transition_article(article_id=article.id, new_status="archived")


@pytest.mark.django_db
class TestGenerateTags:
    def test_generate_tags_for_article_without_tags(self):
        article = ArticleFactory(title="Login Authentication Error", tags=[])
        result = generate_tags(article_id=article.id)
        assert len(result) > 0
        article.refresh_from_db()
        assert article.tags == result

    def test_generate_tags_skips_when_tags_exist(self):
        article = ArticleFactory(tags=["existing", "tags"])
        result = generate_tags(article_id=article.id)
        assert result == ["existing", "tags"]  # unchanged

    def test_generate_tags_not_found(self):
        with pytest.raises(NotFoundError):
            generate_tags(article_id=uuid.uuid4())


@pytest.mark.django_db
class TestDramatiqTaskQueuing:
    def setup_method(self):
        self.broker = dramatiq.get_broker()
        self.broker.flush_all()

    def test_create_article_without_tags_queues_task(self):
        create_article(
            title="Login Guide",
            content="How to login",
            category="auth",
            tags=[],
            author_name="John",
        )
        queue = self.broker.queues["default"]
        assert queue.qsize() > 0

    def test_create_article_with_tags_skips_queue(self):
        create_article(
            title="Login Guide",
            content="How to login",
            category="auth",
            tags=["login"],
            author_name="John",
        )
        queue = self.broker.queues["default"]
        assert queue.qsize() == 0
