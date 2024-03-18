from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import searchProfiles, paginateProfiles
from authlib.integrations.django_client import OAuth
import json
from urllib.parse import quote_plus, urlencode
from django.urls import reverse
from django.conf import settings

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    authorize_url=f"https://{settings.AUTH0_DOMAIN}/authorize",
    authorize_params=None,
    token_url=f"https://{settings.AUTH0_DOMAIN}/oauth/token",
    userinfo_endpoint=f"https://{settings.AUTH0_DOMAIN}/userinfo",
    userinfo_params=None,
    client_kwargs={
        "scope": "openid profile email",
    },
)



def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("accounts")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("projects")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )


def profiles(request):
    profiles, search_query = searchProfiles(request)

    custom_range, profiles = paginateProfiles(request, profiles, 3)

    context = {'profiles':profiles, 'search_query': search_query, 'custom_range': custom_range}

    return render(
        request,
        "users/profiles.html",
        context
    )


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)

    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    

    context = {'profile': profile, 'topSkills': topSkills, 'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context)

def userAccount(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    context = {'profile':profile, 'skills': skills, 'projects':projects, "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4)}
    return render(request, 'users/account.html', context)


@login_required(login_url="login")
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid:
            form.save()
            return redirect('account')

    context = {'form':form}
    return render(request, 'users/profile_form.html', context)

@login_required(login_url='login')
def createSkill(request):
    form = SkillForm()
    profile = request.user.profile
    
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill has been successfully!')
        return redirect('account')
    
    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url="login")
def editSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid:
            form.save()
            messages.info(request, 'Skill has been updated')
            return redirect('account')

    context = {'form':form}
    return render(request, 'users/skill_form.html', context)

@login_required(login_url="login")
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill has been deleted successfully')
        return redirect('account')
    context = {'object':skill}
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequest = profile.messages.all()
    unreadCount = messageRequest.filter(is_read=False).count()
    context = {'messageRequest': messageRequest, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)

@login_required(login_url='login')
def messageRead(request, pk):
    profile = request.user.profile
    messageCom = profile.messages.get(id=pk)
    if messageCom.is_read == False:
        messageCom.is_read = True
        messageCom.save()
    context = {'messageCom': messageCom}
    return render(request, 'users/message.html', context)

def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None


    if request.method == "POST":
        form = MessageForm(request.POST)
        
        if form.is_valid:
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.name

            message.save()

            messages.success(request, 'Message Sent Successfully')
            return redirect('user-profile', pk)
    
    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/send_message.html', context)


