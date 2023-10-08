from django.contrib import admin
from .models import Questions, Exam, DifficultyLevel, QuestionType, Otp, UserProfile, PurchasedDate, UserResponse, SliderImage
# Register your models here.

admin.site.register(Questions)
admin.site.register(Exam)
admin.site.register(DifficultyLevel)
admin.site.register(QuestionType)
admin.site.register(Otp)
admin.site.register(UserProfile)
admin.site.register(PurchasedDate)
admin.site.register(UserResponse)
admin.site.register(SliderImage)