from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Exam)
admin.site.register(ExamAnswer)
admin.site.register(Examinee)
admin.site.register(ExamineeRecord)
admin.site.register(ExamineePaper)
admin.site.register(ExamPaper)
