import pytest

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from pytest_django.asserts import assertRedirects

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Доступность страниц для анонима"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_author_cant_delete_comments_of_others(admin_client, name, comment):
    """Автор чужие комменты не может трогать"""
    url = reverse(name, args=(comment.pk,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_news_available_for_anonymous(client, news):
    """Аноним читает новости"""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comments_for_anonymous(client, comment, name):
    """Аноним читает комменты, но не редактирует или удаляет"""
    url = reverse(name, args=(comment.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'),)
def test_comments_for_author(author_client, comment, name):
    """Автор читает и удаляет свои комменты"""
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
