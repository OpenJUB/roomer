from django.db import models
from roomer.models import UserProfile


class Question(models.Model):
    creator = models.ForeignKey(UserProfile, related_name='questions')
    question_text = models.CharField(max_length=160)

    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    answer_text = models.TextField()
    answered_by = models.ForeignKey(UserProfile, related_name='answers', null=True, blank=True)

    def __str__(self):
        return self.question_text