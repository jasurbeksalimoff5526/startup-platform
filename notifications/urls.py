from django.urls import path
from .views import NotificationListAPIView, UnreadNotificationListAPIView, MarkNotificationAsReadAPIView, MarkAllNotificationsAsReadAPIView, UnreadNotificationCountAPIView


urlpatterns = [
    path("", NotificationListAPIView.as_view()),
    path("unread/", UnreadNotificationListAPIView.as_view()),
    path("unread-count/", UnreadNotificationCountAPIView.as_view()),
    path("<uuid:pk>/read/", MarkNotificationAsReadAPIView.as_view()),
    path("read-all/", MarkAllNotificationsAsReadAPIView.as_view()),
]
