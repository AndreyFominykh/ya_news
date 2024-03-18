import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    """Автор"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Логин автора"""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    """Новость"""
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(author, news):
    """Коммент"""
    return Comment.objects.create(
        news=news,
        author=author,
        text='текст коммента'
    )


@pytest.fixture
def form_data():
    return {'title': 'Заголовк теста', 'text': 'Текст теста'}


@pytest.fixture
def test_user_cant_use_bad_words():
    return {'text': f'Текст {BAD_WORDS[0]} Текст'}


@pytest.fixture
def comments_in_tests(news, author):
    today = timezone.now()
    for index in range(2):
        all_comments = Comment.objects.create(news=news, author=author,
                                              text=f'Текст {index}')
        all_comments.created = today + timedelta(days=index)
        all.comments.save()
    return all_comments


@pytest.fixture
def all_news():
    """Список новостей"""
    today = datetime.today()
    all_news = [News(title=f'Новость {index}', text='Текст',
                     date=today-timedelta(days=index),)
                for index in range(12)]
    return News.objects.bulk_create(all_news)
