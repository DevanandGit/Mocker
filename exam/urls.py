from django.urls import path
from .views import (RegularUserRegistration, RegularUserLoginView, RegularUserLogoutView, 
                    AdminRegistrationView, AdminLoginView, AdminLogoutView,
                    QuestionListCreateAPIView, QuestionRetrieveUpdateDestroyAPIView,ExamListCreateAPIView, 
                    ExamRetrieveUpdateDestroyAPIView, AddQuestionstoExam,
                    ChangePasswordView, PasswordResetRequest, CheckOTP, ResetPasswordView,
                    AssignExam, UserProfileView, PurchaseHistoryView, UserExamResponseAdd, 
                    QuestionTypeListCreateAPIView, QuestionTypeRetrieveUpdateDestroyAPIView, 
                    DifficultyLevelListCreateAPIView, DifficultyLevelRetrieveUpdateDestroyAPIView,
                    SliderImageAdd, SliderImageRetrieveUpdateDestroyView, FeedbackView, PrivacyPolicy, TermsAndConditions, UserRegistrationThroughExcel)
from rest_framework.routers import DefaultRouter
from .views import current_datetime
urlpatterns = [
    path('user-reg/', RegularUserRegistration.as_view(), name = 'user-reg'),
    path('user-login/', RegularUserLoginView.as_view(), name = 'user-login'),
    path('user-logout/', RegularUserLogoutView.as_view(), name = 'user-logout'),

    path('admin-reg/', AdminRegistrationView.as_view(), name = 'admin-reg'),
    path('admin-login/', AdminLoginView.as_view(), name = 'admin-login'),
    path('admin-logout/', AdminLogoutView.as_view(), name = 'admin-logout'),

    path('question-add-list/', QuestionListCreateAPIView.as_view(), name='question-add-list'),
    path('question-add-list/<int:id>/', QuestionRetrieveUpdateDestroyAPIView.as_view(), name='question-retrieve-delete'),
    path('exam-add-list/', ExamListCreateAPIView.as_view(), name='exam-add-list'),
    path('exam-add-list/<str:exam_id>/', ExamRetrieveUpdateDestroyAPIView.as_view(), name='exam-retrieve-delete'),
    path('add-question-to-exam/', AddQuestionstoExam.as_view(), name = 'add-question-to-exam'),

    path('questiontype-add-list/', QuestionTypeListCreateAPIView.as_view(), name='questiontype-add-list'),
    path('questiontype-add-list/<int:id>/', QuestionTypeRetrieveUpdateDestroyAPIView.as_view(), name='questiontype-retrieve-delete'),
    path('difficulty_level-add-list/', DifficultyLevelListCreateAPIView.as_view(), name='difficulty_level-add-list'),
    path('difficulty_level-add-list/<int:id>/', DifficultyLevelRetrieveUpdateDestroyAPIView.as_view(), name='difficulty_level-retrieve-delete'),
    path('sliderimageadd/', SliderImageAdd.as_view(), name='sliderimageadd'),
    path('sliderimageadd/<int:images_id>', SliderImageRetrieveUpdateDestroyView.as_view(), name='sliderimageadd'),

    path('assign-exam/', AssignExam.as_view(), name = 'assign-exam'),
    path('current-datetime/', current_datetime, name='current_datetime'),

    path('userlist/<str:username>/', UserProfileView.as_view(), name='user_profile'),
    path('userlist/<str:username>/purchase_history/', PurchaseHistoryView.as_view(), name='purchase_history'),
    path('examresponseadd/', UserExamResponseAdd.as_view(), name='examresponseadd'),

    path('change_password/', ChangePasswordView.as_view(), name='change_password'), 
    path('otp-request/', PasswordResetRequest.as_view(), name='otp-request'),
    path('check-otp/', CheckOTP.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),

    path('feedback-add/', FeedbackView.as_view(), name='feedback-add'),
    path('privacy-policy', PrivacyPolicy.as_view(), name = 'privacy-policy'),
    path('terms-and-conditions', TermsAndConditions.as_view(), name = 'terms-and-conditions'),

    path('reg-as-group/', UserRegistrationThroughExcel.as_view(), name='upload-excel'),


]
