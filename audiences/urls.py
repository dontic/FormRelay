from django.urls import path
from audiences.views import SubscriberCreateView

urlpatterns = [
    path("subscribers/", SubscriberCreateView.as_view(), name="subscriber-create"),
]

