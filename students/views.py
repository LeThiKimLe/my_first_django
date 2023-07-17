from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from students.models import Student
from students.serializers import StudentSerializer


# Create your views here.
@api_view(['GET'])
def getview(request):
    if request.method == 'GET':
        student= Student.objects.all()
        serializer = StudentSerializer(student, many=True)
        return Response(serializer.data)
