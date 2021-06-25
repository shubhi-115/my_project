from django.forms import ModelForm
from .models import Interview, Participant
from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'

class DateTimeInput(forms.DateInput):
    input_type = 'datetime-local'

class InterviewForm(ModelForm):
    class Meta:
        model = Interview
        fields = ['title', 'date', 'start_time', 'end_time']
        widgets = {
            'date': DateInput(),
            'start_time' : DateTimeInput(),
            'end_time' : DateTimeInput()
        }

class ParticipantForm(ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'phone_number', 'college', 'email', 'gender', 'position_applied']
        widgets = {
            'phone_number' : forms.NumberInput()
        }
