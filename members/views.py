from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from members.models import Member
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from members.serializers import UserSerializer, GroupSerializer
# Create your views here.

def members(request):
    mymembers = Member.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
        'mymembers': mymembers
    }
    return HttpResponse(template.render(context, request))


def details(request, slug):
    mymember = Member.objects.get(slug=slug)
    template = loader.get_template('detail.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))

def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())

def testing(request):
    template = loader.get_template('template.html')
    context = {
        'fruits': ['Apple','Banana','Cherry'],
        'bought' : ['Apple', 'Banana', 'Cherry']
    }
    return HttpResponse(template.render(context, request))

class UserViewSet (viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    