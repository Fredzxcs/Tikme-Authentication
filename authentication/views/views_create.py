from rest_framework.response import Response
from rest_framework import status, views
from ..models import *
from ..serializers import *


class RolesListCreateView(views.APIView):
    def get(self, request):
        roles = Roles.objects.all()
        serializer = RolesSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RolesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# CRUD for Status
class StatusListCreateView(views.APIView):
    def get(self, request):
        statuses = Status.objects.all()
        serializer = StatusSerializer(statuses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StatusDetailView(views.APIView):
    def get(self, request, pk):
        status_instance = Status.objects.filter(pk=pk).first()
        if not status_instance:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StatusSerializer(status_instance)
        return Response(serializer.data)

    def put(self, request, pk):
        status_instance = Status.objects.filter(pk=pk).first()
        if not status_instance:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StatusSerializer(status_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        status_instance = Status.objects.filter(pk=pk).first()
        if not status_instance:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
        status_instance.delete()
        return Response({'message': 'Status deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# CRUD for Questions
class QuestionsListCreateView(views.APIView):
    def get(self, request):
        questions = Questions.objects.all()
        serializer = QuestionsSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = QuestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionsDetailView(views.APIView):
    def get(self, request, pk):
        question = Questions.objects.filter(pk=pk).first()
        if not question:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionsSerializer(question)
        return Response(serializer.data)

    def put(self, request, pk):
        question = Questions.objects.filter(pk=pk).first()
        if not question:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionsSerializer(question, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        question = Questions.objects.filter(pk=pk).first()
        if not question:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        question.delete()
        return Response({'message': 'Question deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# CRUD for QuestionList
class QuestionListListCreateView(views.APIView):
    def get(self, request):
        question_lists = QuestionList.objects.all()
        serializer = QuestionListSerializer(question_lists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = QuestionListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionListDetailView(views.APIView):
    def get(self, request, pk):
        question_list = QuestionList.objects.filter(pk=pk).first()
        if not question_list:
            return Response({'error': 'QuestionList not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionListSerializer(question_list)
        return Response(serializer.data)

    def put(self, request, pk):
        question_list = QuestionList.objects.filter(pk=pk).first()
        if not question_list:
            return Response({'error': 'QuestionList not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionListSerializer(question_list, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        question_list = QuestionList.objects.filter(pk=pk).first()
        if not question_list:
            return Response({'error': 'QuestionList not found'}, status=status.HTTP_404_NOT_FOUND)
        question_list.delete()
        return Response({'message': 'QuestionList deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# CRUD for User
class UserListCreateView(views.APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetailView(views.APIView):
    def get(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
