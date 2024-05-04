from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.permissions import IsAdminOrIfAuthenticatedReadOnly
from user.serializers import UserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated & IsAdminOrIfAuthenticatedReadOnly]

    def get_object(self):
        return self.request.user
