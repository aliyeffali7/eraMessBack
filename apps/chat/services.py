from apps.accounts.models import User

from .models import Conversation, Message


def get_or_create_direct_conversation(*, user: User, other: User) -> Conversation:
    existing = (
        Conversation.objects.filter(is_group=False, participants=user).filter(participants=other).first()
    )
    if existing:
        return existing
    conversation = Conversation.objects.create(is_group=False)
    conversation.participants.set([user, other])
    return conversation


def create_group_conversation(*, name: str, creator: User, member_ids: list[int]) -> Conversation:
    conversation = Conversation.objects.create(is_group=True, name=name)
    conversation.participants.add(creator, *User.objects.filter(id__in=member_ids))
    return conversation


def send_message(*, conversation: Conversation, sender: User, text: str) -> Message:
    message = Message.objects.create(conversation=conversation, sender=sender, text=text)
    try:
        _notify_participants(conversation=conversation, sender=sender, text=text)
    except Exception:
        pass
    return message


def _notify_participants(*, conversation: Conversation, sender: User, text: str) -> None:
    from apps.notifications.services import send_push_to_users

    recipient_ids = list(conversation.participants.exclude(id=sender.id).values_list("id", flat=True))
    if not recipient_ids:
        return
    title = conversation.name if conversation.is_group else sender.username
    body = f"{sender.username}: {text}" if conversation.is_group else text
    send_push_to_users(
        user_ids=recipient_ids,
        title=title,
        body=body[:200],
        data={"conversation_id": conversation.id},
    )


def list_conversations_for_user(*, user: User):
    return Conversation.objects.filter(participants=user).order_by("-created_at")


def list_messages(*, conversation: Conversation, after_id: int | None = None):
    qs = conversation.messages.select_related("sender")
    if after_id:
        qs = qs.filter(id__gt=after_id)
    return qs
