from rest_framework import serializers
from course.models import Subject
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subject
        fields = ['s_name', 's_code']