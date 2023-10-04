#All logical functions and inheritance are implemented here.
from django.db.models import DurationField
import random
from rest_framework.response import Response
from django.core.mail import EmailMessage
import json
class CustomDuration(DurationField):
    def format_duration(self, duration):
        formatted_duration = super().format_duration(duration)
        hours, minutes, seconds = formatted_duration.split(":")
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
def add_question(exams, questions, questions_count):
    # for i in range(questions_count):
    #     test = random.choice(questions)
    #     exams.questions.add(test)

    # if exams.questions.count() != questions_count:
    #     remaining = questions_count - exams.questions.count()
    #     for i in range(remaining):
    #         test = random.choice(questions)
    #         exams.questions.add(test)
    question_ids = list(questions.values_list('id', flat=True))
    # Shuffle the list of question IDs to randomize the selection
    random.shuffle(question_ids)
    
    questions_to_add = question_ids[:questions_count]
    print(f"questions to Add:{questions_to_add}")
    # Add selected questions to the exam
    exams.questions.add(*questions_to_add)


#method to send mail.
class Utils:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to = [data['to_email']])
        email.send()
        return Response('Email sent successfully!')
    
#method to generate OTP
def otpgenerator():
    rand_no = [x for x in range(10)]
    code_items_for_otp = []

    for i in range(6):
        num = random.choice(rand_no)
        code_items_for_otp.append(num)
        code_string = "".join(str(item) for item in code_items_for_otp)

    return code_string

#method to validate OTP
def checkOTP(otp, saved_otp_instance):
    if saved_otp_instance.otp == otp:
        return True
    else:
        return False
        

#method to delete OTP
def deleteOTP(saved_otp_instance):
    saved_otp_instance.delete()
    

#need to pass the questions of the created exam to this method. It will create a dictionary 
#with key as 'question_id' and value as 'answers'
def SolutionCreator(questions):
    answers = {}
    for question in questions:
        question_id = question.id
        answer = question.answer
        answers[question_id] = answer
    return answers


#it takes the user-exam-response and solution and perfrom valuation.
def resultvalidator(response, solution, exam):
    mark = 0
    response = json.dumps(response)
    response = json.loads(response)
    response= {int(key): value for key, value in response.items()}
    print(response)
    for question_id in solution:
        if question_id in response:
            if response[question_id] == solution[question_id]:
                mark+=exam.postive_marks
            elif response[question_id] == "":
                pass
            else:
                mark-=exam.negetive_marks
    mark = max(mark, 0)

    return mark
