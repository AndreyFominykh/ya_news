import pytest

from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse


User = get_user_model()


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_count_on_homepage(client):
    """Считаем новости на гл странице"""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_on_homepage(client):
    """Проверяем что новости на гл странице отсортированы"""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    news_dates_sorted = sorted(dates, reverse=True)
    assert news_dates_sorted == dates


@pytest.mark.django_db
def test_comments_sorted_on_detail_page(client, news):
    """комменты на отдельной странцие отсортированы по дате"""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    dates = [comment.created for comment in all_comments]
    sorted_date = sorted(dates)
    assert dates == sorted_date


@pytest.mark.django_db
def test_auth_client_has_form(author_client, news):
    """Авторизованный может писать комменты"""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_anonymous_has_no_form(client, news):
    """Аноним не может писать комменты"""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context
