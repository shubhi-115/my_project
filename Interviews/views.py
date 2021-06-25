from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Interview, InterviewParticipants, Participant
from .forms import InterviewForm, ParticipantForm
from django.core.files.storage import FileSystemStorage
from my_project.settings import EMAIL_HOST_USER
from . import forms
from django.core.mail import send_mail


# Create your views here.
def home(request):
    return render(request, 'interviews/home.html')

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'interviews/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'interviews/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('get_interviews')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def get_interviews(request):
    interviews = Interview.objects.all().order_by('date')
    return render(request , 'interviews/listings.html', { 'interviews':interviews } )


@login_required
def create_interview(request):
    if request.method == 'GET':
        participants = Participant.objects.all()
        return render(request, 'interviews/createInterview.html', {'form':InterviewForm, 'participants' : participants})
    else:
        try:
            form = InterviewForm(request.POST)
            paritipant_one = request.POST['participant_one']
            paritipant_two = request.POST['participant_two']
            if(paritipant_one != "None" and paritipant_two != "None" and (paritipant_one == paritipant_two)):
                participants = Participant.objects.all()
                return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Participant One and Two cannot be same, Press back button above','participants' : participants})
            if(paritipant_one != "None" and paritipant_two != "None"):
                participant_one_instance = Participant.objects.filter(name__icontains=paritipant_one)[0]
                participant_two_instance = Participant.objects.filter(name__icontains=paritipant_two)[0]
                interviews = Interview.objects.all()
                newInterview = form.save(commit=False)
                # Condition to check slot overlap for Participant One
                for inter in interviews:
                    iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                    if(iparticipants.candidate_one == participant_one_instance or iparticipants.candidate_two == participant_one_instance):
                        if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                            participants = Participant.objects.all()
                            return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Participant One already has interview in this time slot, Press back button above','participants' : participants})
                
                # Condition to check slot overlap for Participant Two
                for inter in interviews:
                    iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                    if(iparticipants.candidate_one == participant_two_instance or iparticipants.candidate_two == participant_two_instance):
                        if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                            participants = Participant.objects.all()
                            return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Participant Two already has interview in this time slot, Press back button above','participants' : participants})
                        

                newInterview.save()
                newInterviewParticipants = InterviewParticipants(interview = newInterview, candidate_one = participant_one_instance, candidate_two = participant_two_instance)
                newInterviewParticipants.save()
            elif(paritipant_one != "None" and paritipant_two == "None"):
                participant_one_instance = Participant.objects.filter(name__icontains=paritipant_one)[0]
                interviews = Interview.objects.all()
                newInterview = form.save(commit=False)
                # Condition to check slot overlap
                for inter in interviews:
                    iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                    if(iparticipants.candidate_one == participant_one_instance or iparticipants.candidate_two == participant_one_instance):
                        if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                            participants = Participant.objects.all()
                            return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Participant One already has interview in this time slot, Press back button above','participants' : participants})
                
                newInterview.save()
                newInterviewParticipants = InterviewParticipants(interview = newInterview, candidate_one = participant_one_instance)
                newInterviewParticipants.save()
            elif(paritipant_one == "None" and paritipant_two != "None"):
                participant_two_instance = Participant.objects.filter(name__icontains=paritipant_two)[0]
                interviews = Interview.objects.all()
                newInterview = form.save(commit=False)
                # Condition to check slot overlap
                for inter in interviews:
                    iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                    if(iparticipants.candidate_one == participant_two_instance or iparticipants.candidate_two == participant_two_instance):
                        if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                            participants = Participant.objects.all()
                            return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Participant Two already has interview in this time slot, Press back button above','participants' : participants})
                newInterview.save()
                newInterviewParticipants = InterviewParticipants(interview = newInterview, candidate_two = participant_two_instance)
                newInterviewParticipants.save()
            else:
                newInterview = form.save(commit=False)
                newInterview.save()
                newInterviewParticipants = InterviewParticipants(interview = newInterview)
                newInterviewParticipants.save()
            return redirect('get_interviews')
        except ValueError:
            participants = Participant.objects.all()
            return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Bad Data Passed','participants' : participants})

@login_required
def delete_interview(request, interview_id):
    instance = Interview.objects.get(id = interview_id)
    instance.delete()
    interviews = Interview.objects.all()
    return render(request , 'interviews/listings.html', { 'interviews':interviews } )

@login_required
def edit_interview(request, interview_id):
    if request.method == 'GET':
        instance = Interview.objects.get(id = interview_id)
        iparticipants = InterviewParticipants.objects.filter(interview = instance)[0]
        participants = Participant.objects.all()
        form = InterviewForm(initial = {
            'title' : instance.title,
            'date' : instance.date,
            'start_time' : instance.start_time,
            'end_time' : instance.end_time
        })
        return render(request , 'interviews/edit_interview.html', { 'form':form, 'participant': iparticipants, 'participants': participants, 'interview': instance} )
    else:
        try:
            instance = Interview.objects.get(id = interview_id)
            form = InterviewForm(request.POST, instance = instance)
            paritipant_one = request.POST['participant_one']
            paritipant_two = request.POST['participant_two']
            if(paritipant_one != "None" and paritipant_two != "None" and (paritipant_one == paritipant_two)):
                participants = Participant.objects.all()
                iparticipants = InterviewParticipants.objects.filter(interview = instance)[0]
                return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Participant One and Two cannot be same, Press back button above','participant': iparticipants, 'participants': participants, 'interview': instance})
            
            newInterview = form.save()
            form.save()
            iparticipants = InterviewParticipants.objects.filter(interview = instance)[0]
            participant_one_instance = Participant.objects.filter(name__icontains=paritipant_one)
            participant_two_instance = Participant.objects.filter(name__icontains=paritipant_two)
            
            if len(participant_one_instance) == 0 and len(participant_two_instance) == 0:
                iparticipants.candidate_one = None
                iparticipants.candidate_two = None
            elif len(participant_one_instance) == 0 and len(participant_two_instance) != 0:
                iparticipants.candidate_one = None
                participant_two_ins = participant_two_instance[0]
                interviews = Interview.objects.all()
                for inter in interviews:
                    if(inter != instance):
                        iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                        if(iparticipants.candidate_one == participant_two_ins or iparticipants.candidate_two == participant_two_ins):
                            if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                                participants = Participant.objects.all()
                                return render(request, 'interviews/edit_interview.html', {'form':InterviewForm(), 'error':'Participant Two already has interview in this time slot, Press back button above','participants' : participants, 'interview': instance})
                 
                iparticipants.candidate_two = participant_two_instance[0]
            elif len(participant_one_instance) != 0 and len(participant_two_instance) == 0:
                iparticipants.candidate_two = None
                participant_one_ins = participant_one_instance[0]
                interviews = Interview.objects.all()
                for inter in interviews:
                    if(inter != instance):
                        iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                        if(iparticipants.candidate_one == participant_one_ins or iparticipants.candidate_two == participant_one_ins):
                            if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                                participants = Participant.objects.all()
                                return render(request, 'interviews/edit_interview.html', {'form':InterviewForm(), 'error':'Participant One already has interview in this time slot, Press back button above','participants' : participants, 'interview': instance})
                    
                iparticipants.candidate_one = participant_one_instance[0]
            else:
                interviews = Interview.objects.all()
                participant_one_ins = participant_one_instance[0]
                participant_two_ins = participant_two_instance[0]

                for inter in interviews:
                    if(inter != instance):
                        iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                        if(iparticipants.candidate_one == participant_one_ins or iparticipants.candidate_two == participant_one_ins):
                            if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                                participants = Participant.objects.all()
                                return render(request, 'interviews/edit_interview.html', {'form':InterviewForm(), 'error':'Participant One already has interview in this time slot, Press back button above','participants' : participants, 'interview': instance})
                
                
                for inter in interviews:
                    if(inter != instance):
                        iparticipants = InterviewParticipants.objects.filter(interview = inter)[0]
                        if(iparticipants.candidate_one == participant_two_ins or iparticipants.candidate_two == participant_two_ins):
                            if (newInterview.start_time >= inter.start_time and newInterview.start_time <= inter.end_time) or (newInterview.end_time >= inter.start_time and newInterview.end_time <= inter.end_time):
                                participants = Participant.objects.all()
                                return render(request, 'interviews/edit_interview.html', {'form':InterviewForm(), 'error':'Participant Two already has interview in this time slot, Press back button above','participants' : participants, 'interview': instance})
                 
                iparticipants.candidate_one = participant_one_instance[0]
                iparticipants.candidate_two = participant_two_instance[0]
            
            iparticipants.save()
            
            return redirect('get_interviews')
        except ValueError:
            participants = Participant.objects.all()
            return render(request, 'interviews/createInterview.html', {'form':InterviewForm(), 'error':'Bad Data Passed','participants' : participants, 'interview': instance})

@login_required
def create_participant(request):
    if request.method == 'GET':
        return render(request, 'interviews/createParticipant.html', {'form':ParticipantForm()})
    else:
        try:
            form = ParticipantForm(request.POST)
            newParticipant = form.save(commit=False)
            newParticipant.save()
            return redirect('get_interviews')
        except ValueError:
            participants = Participant.objects.all()
            return render(request, 'interviews/createParticipant.html', {'form':ParticipantForm(), 'error':'Bad Data Passed'})

@login_required
def list_participants(request):
    participants = Participant.objects.all()
    return render(request , 'interviews/listings_par.html', { 'participants': participants } )

@login_required
def upload_resume(request, pname):
    participants = Participant.objects.all()
    if request.method == "POST":
        file = request.FILES['resumefile']
        fs = FileSystemStorage()
        fs.save(file.name, file)
        participant = Participant.objects.filter(name__icontains=pname)[0]
        participant.resume = file
        participant.save()
        return render(request , 'interviews/listings_par.html', { 'participants': participants } )
    return render(request , 'interviews/listings_par.html', { 'participants': participants } )

@login_required
def interview_detail(request, i_id):
    interview = Interview.objects.filter(id = i_id)[0]
    iparticipants = InterviewParticipants.objects.filter(interview = interview)[0]
    return render(request, 'interviews/interview_detail.html', {'interview': interview, 'participants': iparticipants})

@login_required
def delete_participant(request, p_id):
    instance = Participant.objects.get(id = p_id)
    instance.delete()
    participants = Participant.objects.all()
    return render(request , 'interviews/listings_par.html', { 'participants': participants } )
    
@login_required
def list_resume(request):
    participants = Participant.objects.all()
    return render(request , 'interviews/list_resume.html', { 'participants': participants } )

@login_required
def send_email(request, p_id, i_id):
    instance = Participant.objects.get(id = p_id)
    interview = Interview.objects.filter(id = i_id)[0]
    recepient = str(instance.email)
    subject = str('Interview For ' + interview.title)
    message = str('You have an Interview Scheduled from ' + str(interview.start_time) + ' to ' + str(interview.end_time))
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    iparticipants = InterviewParticipants.objects.filter(interview = interview)[0]
    return render(request, 'interviews/interview_detail.html', {'interview': interview, 'participants': iparticipants})

@login_required
def edit_participant(request, p_id):
    if request.method == 'GET':
        instance = Participant.objects.get(id = p_id)
        participants = Participant.objects.all()
        form = ParticipantForm(initial = {
            'name' : instance.name,
            'phone_number' : instance.phone_number,
            'college' : instance.college,
            'email' : instance.email,
            'gender' : instance.gender,
            'position_applied' : instance.position_applied
        })
        return render(request, 'interviews/editParticipant.html', {'form': form})
    else:
        instance = Participant.objects.get(id = p_id)
        form = ParticipantForm(request.POST, instance = instance)
        newInterview = form.save()
        form.save()
        participants = Participant.objects.all()
        return render(request , 'interviews/listings_par.html', { 'participants': participants } )




