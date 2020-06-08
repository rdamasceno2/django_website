# users/views.py
from rest_framework import generics
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from users.models import CustomUser
from . import models
from . import serializers


class UserListView(generics.ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer


def user(request, id):
    users = get_object_or_404(CustomUser,  pk=id)
    return render(request, 'user.html', {"users": users})
