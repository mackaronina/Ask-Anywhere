import uuid
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from questions_answers.forms import CreateUpdateQuestionForm, SearchQuestionsForm
from questions_answers.models import Question, Answer, Vote

User = get_user_model()


def create_user(username='testuser', password='StrongPass123!'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@example.com')


def create_question(user, title='Hello world?', text='Hello world!'):
    return Question.objects.create(title=title, text=text, user=user)


def create_answer(question, user, text='Answer to question.'):
    return Answer.objects.create(question=question, text=text, user=user)


def create_vote(target, user, is_positive=True):
    ct = ContentType.objects.get_for_model(target)
    return Vote.objects.create(
        content_type=ct,
        object_id=target.pk,
        user=user,
        is_positive=is_positive,
    )


class QuestionModelTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.question = create_question(self.user)

    def test_str_contains_title_and_username(self):
        self.assertIn('Hello world?', str(self.question))
        self.assertIn('testuser', str(self.question))

    def test_get_absolute_url(self):
        url = self.question.get_absolute_url()
        self.assertIn(str(self.question.pk), url)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_has_solution_false_by_default(self):
        self.assertFalse(self.question.has_solution())

    def test_has_solution_true_when_answer_marked(self):
        answer = create_answer(self.question, self.user)
        answer.is_solution = True
        answer.save()
        q = Question.objects.get(pk=self.question.pk)
        self.assertTrue(q.has_solution())


class AnswerModelTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.question = create_question(self.user)
        self.answer = create_answer(self.question, self.user)

    def test_str_contains_text_and_username(self):
        self.assertIn('Answer to question.', str(self.answer))
        self.assertIn('testuser', str(self.answer))

    def test_get_absolute_url_references_question(self):
        url = self.answer.get_absolute_url()
        self.assertIn(str(self.question.pk), url)
        self.assertIn(str(self.answer.pk), url)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_is_solution_false_by_default(self):
        self.assertFalse(self.answer.is_solution)


class VoteModelTest(TestCase):
    def setUp(self):
        self.user = create_user()
        owner = create_user('testowner')
        self.question = create_question(owner)

    def test_positive_vote_increments_rating(self):
        create_vote(self.question, self.user, is_positive=True)
        self.assertEqual(self.question.get_rating(), 1)

    def test_negative_vote_decrements_rating(self):
        create_vote(self.question, self.user, is_positive=False)
        self.assertEqual(self.question.get_rating(), -1)

    def test_get_rating_zero_no_votes(self):
        self.assertEqual(self.question.get_rating(), 0)

    def test_is_negative_property(self):
        vote = create_vote(self.question, self.user, is_positive=False)
        self.assertTrue(vote.is_negative)

    def test_duplicate_vote_raises_integrity_error(self):
        create_vote(self.question, self.user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            create_vote(self.question, self.user)

    def test_get_vote_returns_vote_for_user(self):
        vote = create_vote(self.question, self.user)
        self.assertEqual(self.question.get_vote(self.user), vote)

    def test_get_vote_returns_none_for_anonymous(self):
        self.assertIsNone(self.question.get_vote(AnonymousUser()))

    def test_get_absolute_url(self):
        vote = create_vote(self.question, self.user)
        self.assertEqual(vote.get_absolute_url(), self.question.get_absolute_url())

    def test_str_contains_is_positive_and_username(self):
        vote = create_vote(self.question, self.user)
        self.assertIn('testuser', str(vote))
        self.assertIn('Positive', str(vote))
        vote.is_positive = False
        self.assertIn('Negative', str(vote))


class CreateUpdateQuestionFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'title': 'Hello world?',
            'text': 'Hello world!'
        }
        form = CreateUpdateQuestionForm(data=data)
        self.assertTrue(form.is_valid())

    def test_title_must_end_with_question_mark(self):
        data = {
            'title': 'Hello world',
            'text': 'Hello world!'
        }
        form = CreateUpdateQuestionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class SearchQuestionsFormTest(TestCase):
    def test_empty_form_is_valid(self):
        form = SearchQuestionsForm(data={})
        self.assertTrue(form.is_valid(), form.errors)


class IndexViewTest(TestCase):
    def test_index_returns_200(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)

    def test_index_contains_recent_questions_and_answers(self):
        user = create_user()
        question = create_question(user)
        answer = create_answer(question, user)
        resp = self.client.get(reverse('index'))
        self.assertIn('recent_questions', resp.context)
        self.assertIn('recent_answers', resp.context)
        self.assertIn(question, resp.context['recent_questions'])
        self.assertIn(answer, resp.context['recent_answers'])


class QuestionsIndexViewTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.q1 = create_question(self.user, title='What is Django?')
        self.q2 = create_question(self.user, title='What is Flask?')

    def test_list_returns_200(self):
        resp = self.client.get(reverse('questions_index'))
        self.assertEqual(resp.status_code, 200)

    def test_list_shows_questions(self):
        resp = self.client.get(reverse('questions_index'))
        self.assertIn('questions', resp.context)
        self.assertIn(self.q1, resp.context['questions'])
        self.assertIn(self.q2, resp.context['questions'])

    def test_search_by_term(self):
        resp = self.client.get(reverse('questions_index'), {'term': 'django'})
        self.assertIn('questions', resp.context)
        self.assertIn(self.q1, resp.context['questions'])
        self.assertNotIn(self.q2, resp.context['questions'])

    def test_filter_has_solution(self):
        answer = create_answer(self.q1, self.user)
        answer.is_solution = True
        answer.save()
        resp = self.client.get(reverse('questions_index'), {'has_solution': True})
        self.assertIn('questions', resp.context)
        self.assertIn(self.q1, resp.context['questions'])
        self.assertNotIn(self.q2, resp.context['questions'])


class QuestionDetailViewTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.question = create_question(self.user)

    def test_detail_returns_200(self):
        url = reverse('question_detail', kwargs={'pk': self.question.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_detail_404_for_unknown_pk(self):
        url = reverse('question_detail', kwargs={'pk': uuid.uuid4()})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_detail_contains_question(self):
        url = reverse('question_detail', kwargs={'pk': self.question.pk})
        resp = self.client.get(url)
        self.assertIn('question', resp.context)
        self.assertEqual(self.question, resp.context['question'])


class CreateQuestionViewTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.url = reverse('create_question')

    def test_get_returns_200_for_authenticated(self):
        self.client.login(username='testuser', password='StrongPass123!')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))

    def test_post_creates_question(self):
        self.client.login(username='testuser', password='StrongPass123!')
        data = {
            'title': 'What is Django?',
            'text': 'What is Django.',
            'tags': 'Django, Python'
        }
        self.client.post(self.url, data)
        self.assertTrue(Question.objects.filter(title='What is Django?', user=self.user).exists())

    def test_post_invalid_title_does_not_create(self):
        self.client.login(username='testuser', password='StrongPass123!')
        data = {
            'title': 'What is Django.',
            'text': 'What is Django.',
            'tags': 'Django, Python'
        }
        self.client.post(self.url, data)
        self.assertFalse(Question.objects.filter(title='What is Django.', user=self.user).exists())


class UpdateQuestionViewTest(TestCase):
    def setUp(self):
        self.owner = create_user('owner')
        self.other = create_user('other')
        self.question = create_question(self.owner)
        self.url = reverse('update_question', kwargs={'pk': self.question.pk})

    def test_owner_can_get_update_page(self):
        self.client.login(username='owner', password='StrongPass123!')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_non_owner_gets_404(self):
        self.client.login(username='other', password='StrongPass123!')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))

    def test_owner_can_update_question(self):
        self.client.login(username='owner', password='StrongPass123!')
        data = {
            'title': 'What is Python?',
            'text': 'What is Python.',
            'tags': 'Python'
        }
        self.client.post(self.url, data)
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'What is Python?')


class DeleteQuestionViewTest(TestCase):
    def setUp(self):
        self.owner = create_user('owner')
        self.other = create_user('other')
        self.question = create_question(self.owner)
        self.url = reverse('delete_question', kwargs={'pk': self.question.pk})

    def test_owner_can_delete(self):
        self.client.login(username='owner', password='StrongPass123!')
        self.client.post(self.url)
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())

    def test_non_owner_cannot_delete(self):
        self.client.login(username='other', password='StrongPass123!')
        self.client.post(self.url)
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())

    def test_anonymous_cannot_delete(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())


class CreateAnswerViewTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.question = create_question(self.user)
        self.url = reverse('create_answer', kwargs={'pk': self.question.pk})

    def test_anonymous_redirected(self):
        data = {
            'text': 'Answer to question.'
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))
        self.assertFalse(Answer.objects.exists())

    def test_authenticated_user_can_create_answer(self):
        self.client.login(username='testuser', password='StrongPass123!')
        data = {
            'text': 'Answer to question.'
        }
        self.client.post(self.url, data)
        self.assertTrue(Answer.objects.filter(question=self.question, user=self.user).exists())


class MarkAnswerViewTest(TestCase):
    def setUp(self):
        self.owner = create_user('owner')
        self.other = create_user('other')
        self.question = create_question(self.owner)
        self.answer = create_answer(self.question, self.other)
        self.url = reverse('update_answer_mark', kwargs={'pk': self.answer.pk})

    def test_question_owner_can_mark_and_unmark_answer(self):
        self.client.login(username='owner', password='StrongPass123!')
        self.client.post(self.url, {'is_solution': True})
        self.answer.refresh_from_db()
        self.assertTrue(self.answer.is_solution)
        self.client.post(self.url, {'is_solution': False})
        self.answer.refresh_from_db()
        self.assertFalse(self.answer.is_solution)

    def test_non_owner_cannot_mark_answer(self):
        self.client.login(username='other', password='StrongPass123!')
        resp = self.client.post(self.url, {'is_solution': True})
        self.assertEqual(resp.status_code, 404)
        self.answer.refresh_from_db()
        self.assertFalse(self.answer.is_solution)

    def test_anonymous_cannot_mark(self):
        resp = self.client.post(self.url, {'is_solution': True})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))
        self.assertFalse(self.answer.is_solution)


class VotingViewTest(TestCase):
    def setUp(self):
        self.owner = create_user('owner')
        self.voter = create_user('voter')
        self.question = create_question(self.owner)
        self.vote_url = reverse('create_vote_question', kwargs={'pk': self.question.pk})
        self.delete_url = reverse('delete_vote_question', kwargs={'pk': self.question.pk})

    def test_authenticated_user_can_vote(self):
        self.client.login(username='voter', password='StrongPass123!')
        self.client.post(self.vote_url, {'is_positive': True})
        self.assertTrue(Vote.objects.filter(object_id=self.question.pk, user=self.voter, is_positive=True).exists())

    def test_owner_cannot_vote_for_own_question(self):
        self.client.login(username='owner', password='StrongPass123!')
        resp = self.client.post(self.vote_url, {'is_positive': True})
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Vote.objects.exists())

    def test_anonymous_cannot_vote(self):
        resp = self.client.post(self.vote_url, {'is_positive': True})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))
        self.assertFalse(Vote.objects.exists())

    def test_user_can_delete_vote(self):
        self.client.login(username='voter', password='StrongPass123!')
        self.client.post(self.vote_url, {'is_positive': True})
        self.assertTrue(Vote.objects.filter(object_id=self.question.pk, user=self.voter).exists())
        self.client.post(self.delete_url)
        self.assertFalse(Vote.objects.filter(object_id=self.question.pk, user=self.voter).exists())

    def test_revote_updates_existing_vote(self):
        self.client.login(username='voter', password='StrongPass123!')
        self.client.post(self.vote_url, {'is_positive': True})
        self.assertTrue(Vote.objects.filter(object_id=self.question.pk, user=self.voter, is_positive=True).exists())
        self.client.post(self.vote_url, {'is_positive': False})
        self.assertTrue(Vote.objects.filter(object_id=self.question.pk, user=self.voter, is_positive=False).exists())
        self.assertEqual(Vote.objects.count(), 1)


class RandomQuestionViewTest(TestCase):
    def test_redirects_to_questions_index_when_empty(self):
        resp = self.client.get(reverse('random_question'))
        self.assertRedirects(resp, reverse('questions_index'), 302)

    def test_redirects_to_question_when_exists(self):
        user = create_user()
        question = create_question(user)
        resp = self.client.get(reverse('random_question'))
        self.assertRedirects(resp, question.get_absolute_url(), 302)
