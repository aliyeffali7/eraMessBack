from django.urls import path

from .views import (
    ConversationListView,
    CreateGroupConversationView,
    MessageListCreateView,
    StartDirectConversationView,
)

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversation-list"),
    path("conversations/direct/", StartDirectConversationView.as_view(), name="conversation-direct"),
    path("conversations/group/", CreateGroupConversationView.as_view(), name="conversation-group"),
    path("conversations/<int:conversation_id>/messages/", MessageListCreateView.as_view(), name="message-list"),
]
