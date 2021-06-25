from django.contrib import admin
from Interviews.models import Participant, Interview, InterviewParticipants

# Register your models here.
admin.site.register(Participant)
admin.site.register(Interview)
admin.site.register(InterviewParticipants)
