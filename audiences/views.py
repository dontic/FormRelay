from rest_framework import generics, permissions
from audiences.models import Subscriber
from audiences.serializers import SubscriberSerializer


class SubscriberCreateView(generics.CreateAPIView):
    """
    Public endpoint to create a new subscriber.
    Automatically records the source from the request Origin/Referer header.
    """

    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.AllowAny]
