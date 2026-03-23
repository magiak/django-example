import uuid

import pytest
from django.test import Client

from .factories import ArticleFactory


@pytest.mark.django_db
class TestCreateArticleAPI:
    def setup_method(self):
        self.client = Client()

    def test_create_article(self):
        response = self.client.post(
            "/api/knowledge/",
            data={
                "title": "Test Article",
                "content": "This is a test article.",
                "category": "general",
                "tags": ["test", "article"],
                "author_name": "John Doe",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Article"
        assert data["status"] == "draft"

    def test_create_article_without_tags(self):
        response = self.client.post(
            "/api/knowledge/",
            data={
                "title": "No Tags",
                "content": "Body",
                "category": "general",
                "author_name": "Jane",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["tags"] == []


@pytest.mark.django_db
class TestListArticlesAPI:
    def setup_method(self):
        self.client = Client()

    def test_list_articles(self):
        ArticleFactory.create_batch(3)
        response = self.client.get("/api/knowledge/")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_filter_by_category(self):
        ArticleFactory(category="auth")
        ArticleFactory(category="billing")
        response = self.client.get("/api/knowledge/?category=auth")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "auth"


@pytest.mark.django_db
class TestGetArticleAPI:
    def setup_method(self):
        self.client = Client()

    def test_get_article(self):
        article = ArticleFactory(title="Find Me")
        response = self.client.get(f"/api/knowledge/{article.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Find Me"

    def test_get_article_not_found(self):
        response = self.client.get(f"/api/knowledge/{uuid.uuid4()}")
        assert response.status_code == 404


@pytest.mark.django_db
class TestUpdateArticleAPI:
    def setup_method(self):
        self.client = Client()

    def test_update_article(self):
        article = ArticleFactory(title="Old")
        response = self.client.put(
            f"/api/knowledge/{article.id}",
            data={
                "title": "New Title",
                "content": "New content",
                "category": "updated",
                "tags": ["new"],
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["title"] == "New Title"

    def test_update_not_found(self):
        response = self.client.put(
            f"/api/knowledge/{uuid.uuid4()}",
            data={
                "title": "X",
                "content": "X",
                "category": "X",
                "tags": [],
            },
            content_type="application/json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestTransitionArticleAPI:
    def setup_method(self):
        self.client = Client()

    def test_transition_status(self):
        article = ArticleFactory(status="draft")
        response = self.client.patch(
            f"/api/knowledge/{article.id}/status",
            data={"status": "published"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "published"

    def test_transition_invalid(self):
        article = ArticleFactory(status="draft")
        response = self.client.patch(
            f"/api/knowledge/{article.id}/status",
            data={"status": "archived"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_transition_not_found(self):
        response = self.client.patch(
            f"/api/knowledge/{uuid.uuid4()}/status",
            data={"status": "published"},
            content_type="application/json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestDeleteArticleAPI:
    def setup_method(self):
        self.client = Client()

    def test_delete_article(self):
        article = ArticleFactory()
        response = self.client.delete(f"/api/knowledge/{article.id}")
        assert response.status_code == 204

    def test_delete_not_found(self):
        response = self.client.delete(f"/api/knowledge/{uuid.uuid4()}")
        assert response.status_code == 404
