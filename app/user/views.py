'''Views for the user API.'''
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

from core.models import UserSession


class CreateUserView(generics.CreateAPIView):
    '''Create a new user in the system.'''
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    '''Create a new auth token for user.'''
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Attempt to get an existing token for the user
        token, created = Token.objects.get_or_create(user=user)

        # If a token already exists, delete and create a new one
        if not created:
            token.delete()
            token = Token.objects.create(user=user)

        # Store the token
        UserSession.objects.update_or_create(
            user=user, defaults={'token': token.key})

        return Response({'token': token.key})


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''Manage the authenticated user.'''
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        '''Retrieve and return the authenticated user.'''
        return self.request.user
