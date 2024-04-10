'''Views for the user API.'''
from rest_framework import authentication
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

from core.models import UserSession
import random
import string


class CreateUserView(generics.CreateAPIView):
    '''Create a new user in the system.'''
    serializer_class = UserSerializer


class TokenAuthentication(authentication.TokenAuthentication):
    model = UserSession
    keyword = 'Token'

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(token=key)
        except self.model.DoesNotExist:
            return None

        return (token.user, token)


class CreateTokenView(ObtainAuthToken):
    '''Create a new auth token for user.'''
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate a random token - not sure about the implementation of creating token.
        token = ''.join(random.choices(
            string.ascii_letters + string.digits, k=40))

        # Store the token in the database
        UserSession.objects.update_or_create(
            user=user, defaults={'token': token})

        return Response({'token': token})


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''Manage the authenticated user.'''
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        '''Retrieve and return the authenticated user.'''
        return self.request.user
