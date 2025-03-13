from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime
from .models import Question, Choice

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        future_question = Question(pub_date=timezone.now() + datetime.timedelta(days=30))
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions older than 1 day.
        """
        old_question = Question(pub_date=timezone.now() - datetime.timedelta(days=1, seconds=1))
        self.assertIs(old_question.was_published_recently(), False)

    def test_question_str(self):
        """
        Test string representation of a Question.
        """
        question = Question(question_text="Sample Question", pub_date=timezone.now())
        self.assertEqual(str(question), "Sample Question")

    def test_choice_str(self):
        """
        Test string representation of a Choice.
        """
        question = Question(question_text="Sample Question", pub_date=timezone.now())
        choice = Choice(choice_text="Sample Choice", question=question)
        self.assertEqual(str(choice), "Sample Choice")

class QuestionIndexViewTests(TestCase):
    def setUp(self):
        # สร้างทั้งคำถามในอดีตและอนาคต
        self.past_question = Question.objects.create(
            question_text="Past question.",
            pub_date=timezone.now() - datetime.timedelta(days=30)
        )
        self.future_question = Question.objects.create(
            question_text="Future question.",
            pub_date=timezone.now() + datetime.timedelta(days=30)
        )

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        # ลบทุกคำถามที่มีในฐานข้อมูล
        Question.objects.all().delete()
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        # ลบคำถามอนาคตออกเพื่อให้มีแค่คำถามในอดีต
        self.future_question.delete()
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [self.past_question])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page.
        """
        # ลบคำถามในอดีตออกเพื่อให้มีแค่คำถามอนาคต
        self.past_question.delete()
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

class VoteViewTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            question_text="Test Question",
            pub_date=timezone.now(),
            rate = 0
        )
        self.choice1 = Choice.objects.create(
            question=self.question,
            choice_text="Choice 1",
            votes=0
        )

    def test_valid_vote(self):
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)),
            {"choice": self.choice1.id}
    )
        self.choice1.refresh_from_db()
        self.question.refresh_from_db()  

        self.assertEqual(self.choice1.votes, 1)
        self.assertEqual(self.question.rate, 1) 
        self.assertRedirects(response, reverse("polls:results", args=(self.question.id,)))


    def test_invalid_vote(self):
        """
        Voting without selecting a choice should return an error message.
        """
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)),
            {}
        )
        self.assertContains(response, "You didn't select a choice.", html=True)

class PrivateViewTest(TestCase):
    def setUp(self):
        self.question1 = Question.objects.create(
            question_text="Test Question1",
            pub_date=timezone.now(),
            rate = 0,
            is_private = True
        )

        self.question2 = Question.objects.create(
            question_text="Test Question2",
            pub_date=timezone.now(),
            rate = 0,
            is_private = False
        )
    def test_private(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        # ลบคำถามอนาคตออกเพื่อให้มีแค่คำถามในอดีต
        response = self.client.get(reverse("polls:private"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [self.question1])