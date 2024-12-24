from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from ..models import *
from ..serializers import *

class GroupListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.headers.get("Accept") == "application/json":
            # API response for fetching groups in JSON format
            groups = Group.objects.all()
            serializer = GroupSerializer(groups, many=True)
            return Response(serializer.data)
        else:
            # Render the HTML template for group management
            return render(request, "groups.html")

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        group.delete()
        return Response(status=204)
