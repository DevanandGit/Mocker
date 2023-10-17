from django.db import models
from .services import CustomDuration
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class RegularUser(AbstractUser):
    username = models.CharField(max_length=100, validators=[RegexValidator(
        r'^(PRP|prp)[1-9]{2}[A-Z]{2}[0-9]{3}$'
    )], unique=True)
    department = models.CharField(max_length=150)
    semester = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Value must be between 1 and 8"),
            MaxValueValidator(8, message="Value must be between 1 and 8"),
        ], null=True)
    no_of_questions_added = models.PositiveIntegerField(default = 0)
    USERNAME_FIELD = 'username'
    class Meta:
        db_table = 'exam_RegularUser'
    


#model to add Difficulty level
class DifficultyLevel(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    difficulty_level = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.difficulty_level}"


#model to add Question Type
class QuestionType(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    question_type = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.question_type}"


#model to add Questions
class Questions(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    added_by = models.ForeignKey(RegularUser, on_delete = models.SET_NULL, null = True, editable=False)
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True)
    question_type = models.ForeignKey(QuestionType, on_delete=models.SET_NULL, null=True)
    passage = models.TextField(blank=True, null=True)
    questions_text = models.TextField(blank=True, null=True)
    questions_text_slug = models.TextField(blank = True, null = True, unique=True, editable = False)
    questions_image = models.ImageField(upload_to='questions/images/', blank=True, null=True) #need to specify the destination in settings.py
    optionA_text = models.TextField(blank=True, null=True)
    optionA_image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    optionB_text = models.TextField(blank=True, null=True)
    optionB_image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    optionC_text = models.TextField(blank=True, null=True)
    optionC_image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    optionD_text = models.TextField(blank=True, null=True)
    optionD_image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    choose = (('A', 'optionA'), ('B', 'optionB'), ('C', 'optionC'), ('D', 'optionD'))
    answer = models.CharField(max_length=1,choices=choose)
    solution_text = models.TextField(blank=True, null=True, editable=True)
    solution_image = models.ImageField(upload_to='questions/images/', blank=True, null=True, editable=True)
    
    def save(self, *args, **kwargs):
        # Automatically set the solution based on the answer
        option_number = self.answer[-1]  # Extract the option number from 'optionX'
        option_text = getattr(self, f'option{option_number}_text')
        option_image = getattr(self, f'option{option_number}_image')
        
        # if not self.solution_text or not self.solution_image:
        if option_image:  # If option is an image
            self.solution_image = f'Option {option_number}: Image - {option_image.url}' #
            # else:  # If option is text
            #     self.solution_text = f'Option {option_number}: {option_text}'

        if not self.questions_text_slug:
            self.questions_text_slug = slugify(self.questions_text)

        super().save(*args, **kwargs)
        self.added_by.no_of_questions_added = Questions.objects.filter(added_by=self.added_by).count()
        self.added_by.save()

    def __str__(self) -> str:
        return f"{self.id}--{self.questions_text}"


#model to add Exams
class Exam(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    exam_id = models.CharField(unique=True,max_length = 6)
    exam_name = models.CharField(max_length=150)
    exam_image = models.ImageField(upload_to='questions/images/', blank=True, null=True)
    duration = CustomDuration()
    instructions = models.TextField()
    questions = models.ManyToManyField(Questions, related_name='questions', blank=True)
    total_marks = models.PositiveIntegerField()
    qualify_score = models.PositiveIntegerField()
    postive_marks = models.PositiveSmallIntegerField(default=0)
    negetive_marks = models.PositiveSmallIntegerField(default=0)
    department = models.CharField(max_length=150, null=True, blank=True)
    semester = models.IntegerField(
        validators=[MinValueValidator(1, message="Value must be between 1 and 8"),
                    MaxValueValidator(8, message="Value must be between 1 and 8"),],
                    null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Make Sure to Set Active-state while creating.")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank = True, null = True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    updated_date =  models.DateTimeField(auto_now=True, blank=True)
    slug_exam = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug_exam:
            self.slug_exam = slugify(self.exam_name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.exam_id}:{self.exam_name}"

    
# models to store otp``
class Otp(models.Model):
    user = models.OneToOneField(RegularUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_validated = models.BooleanField(default=False, blank=True)


#model for UserProfile.It has onetoone relation with User Model
class UserProfile(models.Model):
    user = models.OneToOneField(RegularUser, on_delete=models.CASCADE, related_name='user_profile', null=True, blank=True)
    purchased_exams = models.ManyToManyField(Exam, blank=True, related_name='purchased_exams')

    def __str__(self) -> str:
        return f"{self.user}"
    

class PurchasedDate(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='purchased_dates')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='purchased_dates', null=True, blank=True)
    date_of_purchase = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField()

    def __str__(self) -> str:
        return f"PurchasedDate for {self.user_profile}, Exam: {self.exam}"
    

class UserResponse(models.Model):
    user = models.ForeignKey(RegularUser, on_delete=models.CASCADE, related_name='userresponse')
    exam_id = models.CharField(max_length=50)
    response = models.JSONField(default=dict)
    marks_scored = models.CharField(max_length=4, default='00')
    #  {
    # "1": "A",
    # "2": "C",
    # "3": "B",
    # }
    def __str__(self) -> str:
        return f"{self.userprofile.username}-{self.exam_id}"
    

    # models to add slider image
class SliderImage(models.Model):
    images_id = models.AutoField(primary_key=True,unique=True)
    images = models.ImageField(upload_to='images/', null=True, blank=True)
    
    def clean(self):
        if SliderImage.objects.count() >= 10 and not self.pk:
            raise ValidationError("More Than 10 Images is not possible.")
        return super().clean()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)