from django.contrib import admin
from .models import RegularUser,Questions, Exam, DifficultyLevel, QuestionType, Otp, UserProfile, PurchasedDate, UserResponse, SliderImage
# Register your models here.

class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'questions_text', 'added_by')

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.save()

admin.site.register(Questions, QuestionsAdmin)

admin.site.register(RegularUser)
admin.site.register(Exam)
admin.site.register(DifficultyLevel)
admin.site.register(QuestionType)
admin.site.register(Otp)
admin.site.register(UserProfile)
admin.site.register(PurchasedDate)
admin.site.register(UserResponse)
admin.site.register(SliderImage)