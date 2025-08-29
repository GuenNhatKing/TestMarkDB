from django.db import models
from exams.models import *

# Create your models here.
class Examinee(models.Model):
    name = models.CharField(max_length=128)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.date_of_birth})"


class ExamineeList(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    examinee = models.ForeignKey(Examinee, on_delete=models.CASCADE)
    score = models.FloatField()
    
    def __str__(self):
        return f"{self.examinee.name} - {self.exam.name}: {self.score}"