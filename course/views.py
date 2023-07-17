from django.http import Http404
from django.shortcuts import render
from course.models import Subject
from rest_framework.views import APIView
from course.serializers import SubjectSerializer
from rest_framework.response import Response 
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
# Create your views here.
"""
Cách 1: Đây là kiểu đơn giản nhất, tường minh nhất
Get thì đọc object, sau đó serialize, rồi chuyển qua dạng json
"""
class SubjectList(APIView):
    """
    List all subject, or create a new subject
    """
    def get(self, request, format=None):
        course = Subject.objects.all()
        serializer = SubjectSerializer(course, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    
class SubjectDetail(APIView):
    def get_object(self, pk):
        try:
            return Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            raise Http404
        
    def get(self, request, pk, format=None):
        subject = self.get_object(pk)
        serializer = SubjectSerializer(subject)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        sub= self.get_object(pk)
        serialize = SubjectSerializer(sub, data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        subject = self.get_object(pk)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""
Cách 2: Sử dụng mixin: Là gom mấy biểu hiện thường dùng lại
"""
class SubjectList1(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class SubjectDetail1(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
"""
Cách 3: Gọn hơn nữa, kế thừa một lớp, có tích hợp các mixin vô trong đó luôn
"""
class SubjectList2(generics.ListCreateAPIView):
    queryset= Subject.objects.all()
    serializer_class = SubjectSerializer

class SubjectDetail2(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer()

