from rest_framework import serializers
from .models import (Exam, Questions, PurchasedDate, 
                     UserProfile, UserResponse, DifficultyLevel, 
                     QuestionType, RegularUser, SliderImage)


#validate data of regular user login.
class RegularUserLoginSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=r'^(PRP|prp)[1-9]{2}[A-Z]{2}[0-9]{3}$', help_text = 'Username should be your college reg-number starting with PRP')
    password = serializers.CharField(max_length=128)


#validate data for admin creation.
class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.RegexField(
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'invalid': 'Password must contain at least 8 characters, including uppercase, lowercase, and numeric characters.'
        }
    )
    confirm_password = serializers.CharField(write_only=True)
    username = serializers.EmailField(help_text = 'Enter Email id as username')

    class Meta:
        model = RegularUser
        fields = ['first_name','last_name' , 'username', 'password', 'confirm_password']
        default_related_name = 'admin_users'

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Password mismatch')
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = RegularUser.objects.create_superuser(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],

        )
        return user
    

#validate data for admin login.
class AdminLoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(max_length=128)
        

#serializer to validate Difficulty level
class DifficultyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyLevel
        fields = ('id', 'difficulty_level')

#serializer to validate Question Type
class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ('id', 'question_type')

#serializer to validate Question data
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['id','difficulty_level', 'question_type', 'questions_text', 'questions_image', 'optionA_text', 'optionA_image', 'optionB_text', 'optionB_image', 'optionC_text', 'optionC_image', 'optionD_text', 'optionD_image', 'choose', 'answer', 'solution_text', 'solution_image']


#serializer to validate Exam data
class ExamSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    # questions = QuestionSerializer(many = True, read_only = True)
    class Meta:
        model = Exam
        fields = ['id', 'exam_id','exam_name', 'duration', 'instructions', 'total_marks', 'qualify_score', 'postive_marks', 'negetive_marks','start_date', 'end_date','is_active', 'created_date', 'updated_date','questions', 'questions_count']

    def get_questions_count(self, obj):
        return obj.questions.count()
    
#serializer to validate Exam data in detail
class ExamDetailSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    questions = QuestionSerializer(many = True, read_only = True)
    class Meta:
        model = Exam
        fields = ['id', 'exam_id','exam_name', 'duration', 'instructions', 'questions_count','total_marks', 'qualify_score', 'postive_marks', 'negetive_marks', 'start_date', 'end_date','is_active', 'created_date', 'updated_date', 'questions']

    def get_questions_count(self, obj):
        return obj.questions.count()


class AddQuestionstoExamSerializer(serializers.Serializer):
    exam_id = serializers.CharField(max_length = 6, min_length = 6)
    question_type = serializers.ChoiceField(choices=QuestionType.objects.values_list('id', 'question_type'), required  =False)
    difficulty_level = serializers.ChoiceField(choices=DifficultyLevel.objects.values_list('id', 'difficulty_level'), required = False)
    questions_count = serializers.IntegerField()



# validates the password entered for changing password.
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['old_password','new_password', 'confirm_password']

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Password mismatch')
        return data


#valildates the email entered for sending otp.
class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    class Meta:
        fields = ['email']


# validates the password entered for changing password.
class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.RegexField(
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'invalid': 'Password must contain at least 8 characters, including uppercase, lowercase, and numeric characters.'
        }
    )
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password','confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('password mismatch')
        return data
        

#validates if the otp entered is correct.
class CheckOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(min_length = 6, max_length = 6)


class PurchasedDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedDate
        fields = ['date_of_purchase','expiration_date']


class UserProfileSerializer(serializers.ModelSerializer):
    purchased_exams = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['purchased_exams']


    def get_purchased_exams(self, obj):
        purchased_dates = obj.purchased_dates.filter(exam__isnull=False)
        serialized_purchased_exams = []
        for purchased_date in purchased_dates:
            serialized_purchased_exams.append({
                'exam_id': purchased_date.exam.exam_id,
                'date_of_purchase': purchased_date.date_of_purchase,
                'expiration_date': purchased_date.expiration_date,
            })
        return serialized_purchased_exams
    

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['exam_id','response','marks_scored']


#serializer to validate the userregistration data.
class RegularUserSerializer(serializers.ModelSerializer):
    password = serializers.RegexField(
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            'invalid': 'Password must contain at least 8 characters, including uppercase, lowercase, and numeric characters.'
        }
    )

    confirm_password = serializers.CharField(write_only=True)

    username = serializers.RegexField(regex=r'^(PRP|prp)[1-9]{2}[A-Z]{2}[0-9]{3}$', help_text = 'Enter a valid PRP code')

    purchase_list = UserProfileSerializer(source = 'user_profile', read_only = True)
    exam_response = UserResponseSerializer(read_only = True)
    
    class Meta:
        model = RegularUser
        fields = ['first_name', 'last_name', 'username', 'email','password', 'confirm_password', 'department', 'semester', 'purchase_list', 'exam_response']
    
    def to_representation(self, instance):
        # Include the logged-in user's exam responses in the representation
        representation = super().to_representation(instance)
        user_responses = instance.userresponse.all()
        exam_response_serializer = UserResponseSerializer(user_responses, many=True)
        representation['exam_response'] = exam_response_serializer.data
        return representation

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Password Mismatch')
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = RegularUser.objects.create_user(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            username = validated_data['username'],
            password = validated_data['password'],
            department = validated_data['department'],
            semester = validated_data['semester']

        )
        return user
    

    #validates the uploading images
class SliderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderImage
        fields = ['images_id','images']