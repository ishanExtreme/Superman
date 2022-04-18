from django.contrib.auth.models import User
from tasks.models import Task, History
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    ChoiceFilter,
    BooleanFilter,
    DateFilter,
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class UserCreationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Register User
class UserCreation(mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (AllowAny,)


# Get user via token
class UserGet(mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)


class TaskSerializer(ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "status", "user", "priority"]


class HistorySerializer(ModelSerializer):
    class Meta:
        model = History
        fields = ["task", "previous_status", "new_status", "changed_at"]


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=Task.STATUS_CHOICES)
    completed = BooleanFilter()


class HistoryFilter(FilterSet):
    changed_at = DateFilter()
    previous_status = ChoiceFilter(choices=Task.STATUS_CHOICES)
    new_status = ChoiceFilter(choices=Task.STATUS_CHOICES)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)

    def perform_create(self, serializer):
        # serializer.user = self.request.user
        # serializer.save()
        serializer.save(user=self.request.user)


class HistroryViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HistoryFilter

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return History.objects.filter(
            task=self.kwargs["task_pk"], task__user=self.request.user
        )
