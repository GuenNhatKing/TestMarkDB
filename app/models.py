from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    isVerificated = models.BooleanField(default=False) # Email verificate

class Examinee(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.date_of_birth})"

class Exam(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    exam_date = models.DateField()
    duration = models.DurationField()

    def __str__(self):
        return f"{self.name} ({self.exam_date})"

class ExamineeList(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    examinee = models.ForeignKey(Examinee, on_delete=models.CASCADE)
    score = models.FloatField()
    
    def __str__(self):
        return f"{self.examinee.name} - {self.exam.name}: {self.score}"

class ExamPaper(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    exam_paper_code = models.CharField(max_length=6)
    number_of_questions = models.IntegerField()
    
    def __str__(self):
        return f"{self.exam.name} - Paper {self.exam_paper_code}"

class ExamAnswer(models.Model):
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    answer_number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    
    def __str__(self):
        return f"{self.exam_paper} Q{self.question_number}: A{self.answer_number}"

class ExamineePaper(models.Model):
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE)
    examinee = models.ForeignKey(Examinee, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    answer_number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    mark_result = models.BooleanField()

    def __str__(self):
        mark = "Correct" if self.mark_result else "Wrong"
        return f"{self.examinee.name} - {self.exam_paper} Q{self.question_number}: A{self.answer_number} ({mark})"