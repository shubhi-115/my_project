from django.db import models
from django.utils import timezone
from phone_field import PhoneField

# Create your models here.
class Participant(models.Model):
    name = models.CharField(max_length = 40)
    phone_number = models.CharField(max_length = 40)
    college = models.CharField(max_length = 100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(
        ('M', 'Male'),
        ('F', 'Female'),
    ))
    email = models.CharField(max_length=40, null = True)
    position_applied = models.CharField(max_length = 30, blank = True, null = True)
    resume = models.FileField(null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

class Interview(models.Model):
    title = models.CharField(max_length = 40)
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True) 
    candidates_count = models.IntegerField(default = 0)
    result = models.CharField( max_length=3, choices=(
        ('S', 'Selected'),
        ('R', 'Rejected'),
        ('J', 'Joined'),
        ('DNJ', 'Did Not Join'),
        ('TBD', 'Pending'),), default='TBD' )

class InterviewParticipants(models.Model):
    interview = models.ForeignKey('Interview', related_name='interview', on_delete=models.CASCADE)
    candidate_one = models.ForeignKey('Participant', related_name='pariticipant_one', on_delete = models.SET_NULL, blank=True, null=True)
    candidate_two = models.ForeignKey('Participant', related_name='pariticipant_two', on_delete = models.SET_NULL, blank=True, null=True)

    
