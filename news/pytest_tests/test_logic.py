import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_cant_post_comment(client, news, form_data):
    """Аноним не может отправить комментарий"""
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_post_comment(author, news, author_client, form_data):
    """Авторизованный пользователь может писать коммент"""
    url = reverse('news:detail', kwargs={'pk':news.pk})
    response = author_client.post(url, data=form_data)
    comment = Comment.objects.get()
    comments_count = Comment.objects.count()
    assert comments_count == 1
    assert comment.author == author
    assert comment.text == form_data['text']
    assert comment.news == news
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_comment_hasnt_bad_words(author_client, news):
    """Нельзя ругаться"""
    bad_words_list = {'text': f'Текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_list)
    comment_count = Comment.objects.count()
    assert comment_count == 0
    assert response.context['form'].errors.get('text') == [WARNING]


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, news, form_data, comment):
    """Можно редактировать свои комменты"""
    url = reverse('news:edit', kwargs={'pk': news.pk})
    edit_url = reverse('news:detail', kwargs={'pk': comment.news.pk}) + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, edit_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Можно удалить свой коммент"""
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    comment_count = Comment.objects.count()
    assert comment_count == 0
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment_of_another_user(admin_client, news):
    """Нельзя удалять чужие комменты"""
    url = reverse('news:delete', kwargs={'pk': news.pk})
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(admin_client, comment,
                                                form_data, news):
    """Нельзя редактировать чужие комментарии"""
    url = reverse('news:delete', kwargs={'pk': news.pk})
    response = admin_client.post(url, dara=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != form_data['text']
