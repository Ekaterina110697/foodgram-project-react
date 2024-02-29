from api.pagination import LimitPageNumberPagination
from api.serializers import (SubscribesListSerializer, UserPasswordSerializer,
                             UserProfileSerializer)
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from foodgram.settings import (NEW_PASSWORD_NOT_VALID, SUBSCRIBE_EXISTS,
                               SUBSCRIBE_NO_EXISTS)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscribe, User


class UserSubscribeViewSet(UserViewSet):
    """Вьюсет пользователя.Управление подписками"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        """Распределение прав на действия."""
        if self.action in ('me', 'set_password', 'subscriptions', 'subscribe'):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserProfileSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request, pk=None):
        user = self.request.user
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(NEW_PASSWORD_NOT_VALID,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
            detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(publisher__user=user)
        paginate_page = self.paginate_queryset(subscriptions)
        serializer = SubscribesListSerializer(
            paginate_page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
        )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscribe = Subscribe.objects.filter(user=user, author=author)
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if subscribe.exists():
                return Response(SUBSCRIBE_EXISTS,
                                status=status.HTTP_400_BAD_REQUEST)
            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribesListSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not subscribe.exists():
                return Response(SUBSCRIBE_NO_EXISTS,
                                status=status.HTTP_400_BAD_REQUEST)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
