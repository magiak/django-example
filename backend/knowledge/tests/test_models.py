import pytest

from shared.exceptions import InvalidTransitionError

from .factories import ArticleFactory


@pytest.mark.django_db
class TestArticleModel:
    def test_create_article_defaults(self):
        article = ArticleFactory()
        assert article.status == "draft"
        assert article.id is not None
        assert article.created_at is not None

    def test_create_article_with_empty_tags(self):
        article = ArticleFactory(tags=[])
        assert article.tags == []

    def test_str_representation(self):
        article = ArticleFactory(title="Login Guide", status="draft")
        assert str(article) == "[draft] Login Guide"

    # --- State machine tests ---

    def test_transition_draft_to_published(self):
        article = ArticleFactory(status="draft")
        article.transition_to("published")
        assert article.status == "published"

    def test_transition_published_to_archived(self):
        article = ArticleFactory(status="published")
        article.transition_to("archived")
        assert article.status == "archived"

    def test_transition_published_to_draft(self):
        article = ArticleFactory(status="published")
        article.transition_to("draft")
        assert article.status == "draft"

    def test_transition_archived_to_draft(self):
        article = ArticleFactory(status="archived")
        article.transition_to("draft")
        assert article.status == "draft"

    def test_invalid_transition_draft_to_archived(self):
        article = ArticleFactory(status="draft")
        with pytest.raises(InvalidTransitionError):
            article.transition_to("archived")

    def test_invalid_transition_archived_to_published(self):
        article = ArticleFactory(status="archived")
        with pytest.raises(InvalidTransitionError):
            article.transition_to("published")

    def test_full_lifecycle(self):
        article = ArticleFactory(status="draft")
        article.transition_to("published")
        article.transition_to("archived")
        article.transition_to("draft")
        assert article.status == "draft"
