from django.db import models
from django.contrib.auth.models import User


class QuizCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class DifficultyLevel(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField()

    def __str__(self):
        return self.question_text


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f'{self.user.username} - {self.category.name} - {self.difficulty.name} - {self.score}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.user.username} at {self.timestamp}'

