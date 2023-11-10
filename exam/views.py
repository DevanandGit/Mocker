from django.shortcuts import render
from .serializers import (RegularUserSerializer, QuestionSerializer, ExamSerializer, 
                          RegularUserLoginSerializer, AdminRegistrationSerializer,
                          AdminLoginSerializer, AddQuestionstoExamSerializer,
                          ChangePasswordSerializer,ResetPasswordEmailSerializer,
                          ResetPasswordSerializer,CheckOTPSerializer,
                          UserProfileSerializer, UserResponseSerializer,
                          DifficultyLevelSerializer, QuestionTypeSerializer, ExamDetailSerializer, SliderImageSerializer)
from rest_framework.generics import (CreateAPIView, ListCreateAPIView, 
                            RetrieveUpdateDestroyAPIView, GenericAPIView, 
                            RetrieveAPIView, ListAPIView)
from .models import (Questions, Exam, Otp,
                      UserProfile, PurchasedDate, UserResponse, AbstractOtp,
                      DifficultyLevel, QuestionType, RegularUser, SliderImage)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from .services import (add_question, otpgenerator, Utils,
                       checkOTP, deleteOTP, SolutionCreator, resultvalidator)
from django.db import transaction
from django.contrib.auth.models import User
import logging
from django.http import Http404
from django.http import JsonResponse
from datetime import datetime
from rest_framework.filters import SearchFilter
logger = logging.getLogger(__name__)


#user registration view.need to add token authentication, login while registration. and also need to create login view.
class RegularUserRegistration(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegularUserSerializer
    def post(self, request):
        serializer = RegularUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = serializer.save()
            print(user)
            # Logging in the user after successful registration
            # Generating or retrieving the token for the logged-in user
            if user:
                token, created = Token.objects.get_or_create(user=user)
                response = {
                    "message":"User Registration Successful",
                    "data": serializer.data,
                    "token": token.key,
                }
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = {
                    "message":"User Registration Unsuccessful",
                }
                return Response(response, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#Regular User login view.
class RegularUserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegularUserLoginSerializer

    def post(self, request):
        serializer = RegularUserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=serializer.data['username'], password=serializer.data['password'])
        if user is not None and not user.is_anonymous:
            token, created = Token.objects.get_or_create(user=user)
            print(token)
            response = {"message": "Login Successful", "token": token.key}
            return Response(response, status = status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=400)


#Regular user logout view.
class RegularUserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Delete the token associated with the user
        Token.objects.filter(user=request.user).delete()
        response = {'message': 'You have been successfully logged out.'}
        return Response(response)


#Admin Registration view.
class AdminRegistrationView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = AdminRegistrationSerializer


#Admin Login View.
#Authentication using django default authentication system.
class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminLoginSerializer
    def post(self, request):
        serializer = AdminLoginSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = authenticate(request, username = serializer.data['username'], password = serializer.data['password'])
        if user is not None and user.is_superuser:
            token, created = Token.objects.get_or_create(user=user)
            response = {"message": "Login Successful","token": token.key}
            return Response(response)
        return Response({'error': 'Invalid credentials'}, status=400)


#Admin Logout View.
#endpoint can only be accessed if the user has authentication permission.
class AdminLogoutView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        if request.user.is_superuser:
            Token.objects.filter(user=request.user).delete()
            response = {'message': 'You have been successfully logged out.'}
            return Response(response)
        else:
            return Response("invalid access")
        

#Admin accessible views.
#View to create and List created Questions.
class QuestionListCreateAPIView(ListCreateAPIView):
    serializer_class = QuestionSerializer
    queryset = Questions.objects.all()
    

#View to Look Questions in detail and Delete created Questions.
class QuestionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    queryset = Questions.objects.all()
    lookup_field = 'id'


#View to create and List created Exams.
class ExamListCreateAPIView(ListCreateAPIView):
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()


#View to Look Questions in detail and Delete created Exams.
class ExamRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExamDetailSerializer
    queryset = Exam.objects.all()
    lookup_field = 'exam_id'


#View to create and List created QuestionType
class QuestionTypeListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = QuestionTypeSerializer
    queryset = QuestionType.objects.all()


#View to Look Questions in detail and Delete created QuestionType
class QuestionTypeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = QuestionTypeSerializer
    queryset = QuestionType.objects.all()
    lookup_field = 'id'


#View to create and List created DifficultyLevel
class DifficultyLevelListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DifficultyLevelSerializer
    queryset = DifficultyLevel.objects.all()


#View to Look Questions in detail and Delete created DifficultyLevel
class DifficultyLevelRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DifficultyLevelSerializer
    queryset = DifficultyLevel.objects.all()
    lookup_field = 'id'
    
#View to add questions to exams randomnly
class AddQuestionstoExam(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AddQuestionstoExamSerializer

    def post(self, request):
        serializer = AddQuestionstoExamSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = request.data['exam_id']
        difficulty_level = request.data['difficulty_level']
        question_type = request.data['question_type']
        questions_count = int(request.data['questions_count'])

        try:
            exams = Exam.objects.get(exam_id=exam_id)
        except Exam.DoesNotExist:
            raise Http404("Exam does not exist")
        
        questions = Questions.objects.filter(difficulty_level = difficulty_level, question_type = question_type)

        if questions.count() < questions_count:
            response = {'success': False, 'message': 'Not enough questions available'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        add_question(exams=exams, questions=questions, questions_count=questions_count)

        # if exams.questions.count() != questions_count: #change the number according to the number of questions
        #     add_question(exams=exams, questions=questions, questions_count=questions_count)

        response = {'success':True,'message': 'Questions added successfully'}

        return Response(response, status=status.HTTP_200_OK)


#view to assign a exam to a user.
class AssignExam(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        #get exam id and username of the user.
        username = request.data.get('username')
        exam_id = request.data.get('exam_id')
        
        #get associated user and examprint
        try:
            exam = Exam.objects.get(exam_id = exam_id)
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        except Exam.DoesNotExist:
            return Response("Exam not found", status=status.HTTP_404_NOT_FOUND)
                
        duration = int(request.data.get('duration')) #duration in days
        
        date_of_purchase = timezone.now()
        expiration_date = date_of_purchase + timezone.timedelta(days=duration)

        user_profile, created = UserProfile.objects.get_or_create(user = user)
        user_profile.purchased_exams.add(exam)

        purchased_date = PurchasedDate.objects.create(user_profile=user_profile,
                                                      exam = exam, 
                                                        date_of_purchase=timezone.now(),
                                                        expiration_date = expiration_date)
        purchased_date.save()

        return Response("Exam purchased successfully", status=status.HTTP_200_OK)

# view to change password by user
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    def post(self, request):
        serializer = ChangePasswordSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if user.check_password(serializer.data['old_password']):
            user.set_password(serializer.data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)    


#view to Request OTP.
class PasswordResetRequest(GenericAPIView):
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):
        serializer = ResetPasswordEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data['email']
        user = RegularUser.objects.filter(email=email).first()
        print(user)
        if user:
            with transaction.atomic():
                otp_record, created = Otp.objects.get_or_create(user=user)
                abstract_otp_record, created = AbstractOtp.objects.get_or_create(user = user)

                if not created:
                    # An OTP record already exists, delete it and create a new one
                    otp_record.delete()
                    otp_record = Otp.objects.create(user=user)

                otp = otpgenerator()
                abstract_otp = otpgenerator()
                print(abstract_otp)
                abstract_otp_record.abstract_otp = abstract_otp
                abstract_otp_record.save()
                otp_record.otp = otp
                otp_record.otp_validated = False
                otp_record.save()

                email_subject = 'Reset your password'
                email_body = f"Hello,\n\nThis is your one-time password for resetting your account's password:\n\n**{otp}**\n\nUse this OTP within the next 30 minutes to complete the password reset process."

                # Prepare email data and send it
                data = {'email_body': email_body, 'to_email': user.email, 'email_subject': email_subject}
                try:
                    Utils.send_email(data)
                    response = {'success': True,
                                'message': "OTP SENT SUCCESSFULLY",
                                'validation_id':abstract_otp}
                    return Response(response, status=status.HTTP_200_OK)

                except Exception as e:
                    logger.error(str(e))
                    return Response({'error': 'An error occurred while sending the email.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'success': False, 'message': "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


#view to validate OTP
class CheckOTP(APIView):
    serializer_class = CheckOTPSerializer

    def post(self, request):
        serializer = CheckOTPSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        otp = self.request.query_params.get('otp')
        abstract_otp = self.request.query_params.get('validation_id')
        try:
            abstract_otp = AbstractOtp.objects.get(abstract_otp = abstract_otp)
            user = abstract_otp.user
        except AbstractOtp.DoesNotExist:
            return Response({"OTP validation Failed"}, status=status.HTTP_401_UNAUTHORIZED )
        
        saved_otp = Otp.objects.get(user = user)
        
        if checkOTP(otp=otp, saved_otp_instance=saved_otp):
            saved_otp.otp_validated = True
            saved_otp.save()
            return Response({'success':True, 'message':"OTP VERIFICATION SUCCESSFULL"}, status=status.HTTP_200_OK)

        else:
            return Response({'success':False, 'message':"INVALID OTP"}, status=status.HTTP_400_BAD_REQUEST)
           


#View to reset password through OTP
class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        otp = self.request.query_params.get('otp')
        abstract_otp = self.request.query_params.get('validation_id')
        try:
            abstract_otp = AbstractOtp.objects.get(abstract_otp = abstract_otp)
            user = abstract_otp.user
        except AbstractOtp.DoesNotExist:
            return Response({"Unauthorised User. Can't Reset Password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            otp = Otp.objects.get(user = user)
        except Otp.DoesNotExist:
            return Response({"Unauthorised User. Can't Reset Password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if otp.otp_validated == True:
            pass
        else:
            response = {
                "message": "OTP Not Validated"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        user = RegularUser.objects.filter(username=user).first()
        otp_instance = Otp.objects.get(user = user)

        if otp_instance.otp_validated == True:
            password  = request.data['password']
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)
            otp_instance.delete()
            
            return Response({'success':True, 'message':"Password Changed Succesfully"}, status=status.HTTP_200_OK)

        else:
            return Response({'success':False, 'message':"verify OTP First"}, status=status.HTTP_400_BAD_REQUEST)


#User Profile View.
class UserProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RegularUserSerializer
    lookup_field = 'username'
    def get_queryset(self):
        # Only allow the user to access their own instance
        print(self.request.user)
        return RegularUser.objects.filter(username=self.request.user.username)


#show the purchased history.
class PurchaseHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    def get_queryset(self): 
        return UserProfile.objects.filter(user = self.request.user)
    

#view to add ExamResponse of User.
class UserExamResponseAdd(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        serializer = UserResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        exam_id = validated_data.get('exam_id')
        user_response_data = validated_data.get('response')

        try:
            exam = Exam.objects.get(exam_id =  exam_id)
            # print(exam.questions.all())
        except Exam.DoesNotExist:
            response = {
                "message" : "Exam Not Found"
            }
            return Response(response, status = 400)
        
        questions = exam.questions.all()
        print(questions)
        solution = SolutionCreator(questions=questions)
        print(solution)
        marks = resultvalidator(response=user_response_data, solution=solution, exam=exam)
                                
        try:
            user_response = UserResponse.objects.create(
                user=user,
                exam_id=exam_id,
                response=user_response_data,
                marks_scored=marks,
            )

            response = {
                "message": "User response added successfully",
                'data': {
                    'exam_id': exam_id,
                    'response':user_response_data,
                    'marks_scored': marks,
                },
                'status': status.HTTP_201_CREATED
            }
            return Response(response, status=status.HTTP_201_CREATED)

        except:
            return Response("User not found", status=status.HTTP_401_UNAUTHORIZED)


#api to return the current date and time
def current_datetime(request):
    current_time = datetime.now()
    response_data = {
        'current_datetime': current_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return JsonResponse(response_data)


class SliderImageAdd(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SliderImageSerializer
    queryset = SliderImage.objects.all()
    
    
class SliderImageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = SliderImageSerializer
    queryset = SliderImage.objects.all()
    lookup_field = "images_id"
