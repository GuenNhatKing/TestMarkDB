from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Examinee)
admin.site.register(Exam)
admin.site.register(ExamineeRecord)
admin.site.register(ExamPaper)
admin.site.register(ExamAnswer)
admin.site.register(ExamineePaper)
admin.site.register(ActionRequest)
admin.site.register(OTPRequest)
