from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.query import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm



"""rooms = [
    {'id': 1, 'name': "Python StudyBud"},
    {'id': 2, 'name': "Front-end Design"},
    {'id': 3, 'name': "We can choose a topic together"},
]"""

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META.HTTP_REFERER)
        else: 
            redirect('home')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except Exception as _:
            messages.error(request, "You need to register")
        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Please, check your password")
    context = {"page": page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    if request.user.is_authenticated:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META.HTTP_REFERER)
        else: 
            redirect('home')
    
    form = MyUserCreationForm()
    if request.method == "POST":  
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "The account creation data you supplied is invalid")

    context = {"form": form}
    return render(request, 'base/login_register.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=int(pk))

    rooms = user.room_set.all().order_by('-created')
    room_messages = user.message_set.all().order_by('-created')
    topics = Topic.objects.all()

    context = {"user": user, "rooms": rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    topics = Topic.objects.all()[0:5]

    if q := request.GET.get('q'):
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
        room_messages = Message.objects.filter(
            Q(user__username__icontains=q) |
            Q(room__name__icontains=q) |
            Q(room__description__icontains=q) |
            Q(body__icontains=q)
        ).order_by('-created')[0:7]
    else:
        rooms = Room.objects.all()
        room_messages = Message.objects.all().order_by('-created')[0:7]

    
    room_count = rooms.count()
    context = {"rooms": rooms, "topics": topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def topicsPage(request):
    if q := request.GET.get("q"):
        topics = Topic.objects.filter(name__icontains=q)
    else:
        topics = Topic.objects.all()
    context = {"topics": topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all().order_by('-created')
    context = {"room_messages": room_messages}
    return render(request, 'base/activity.html', context)

def room(request, pk):
    room = Room.objects.get(id=int(pk))
    participants = room.participants.all()
    if request.method == "POST":
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants
        room.participants.add(request.user)
        # return redirect('room', pk=room.id)
    
    room_messages = room.message_set.all().order_by('created')
    context = {"room": room, "room_messages": room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        topic = request.POST.get("topic")
        topic, _ = Topic.objects.get_or_create(name=topic)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")
    
    topics = Topic.objects.all()
    context = {'form': form, "topics": topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=int(pk))
    if request.user != room.host:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META.HTTP_REFERER)
        else: 
            redirect('home')

    form = RoomForm(instance=room)
    if request.method == "POST":
        room.name = request.POST.get("name")
        topic = request.POST.get("topic")
        room.topic, _ = Topic.objects.get_or_create(name=topic)
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    topics = Topic.objects.all()
    context = {'form': form, "topics": topics, "room": room}
    return render(request, 'base/update_room.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=int(pk))
    if request.user != room.host:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META.HTTP_REFERER)
        else: 
            redirect('home')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, rmid, msgid):
    room = Room.objects.get(id=int(rmid))
    if message := Message.objects.get(id=int(msgid), room=int(rmid)):
        message.delete()
    if Message.objects.filter(user=request.user, room=room).count() == 0:
        room.participants.remove(request.user)
    return redirect('room', pk=rmid)

@login_required(login_url="login")
def updateProfile(request):
    user = request.user
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=str(user.id))
    else:
        form = UserForm(instance=user)

    context = {"form": form}
    return render(request, 'base/update_user.html', context)