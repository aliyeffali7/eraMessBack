from django.db.models import Max
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import User

from .models import Conversation, Message, ReadMarker


def get_or_create_direct_conversation(*, user: User, other: User) -> Conversation:
    existing = (
        Conversation.objects.filter(is_group=False, participants=user)
        .filter(participants=other)
        .first()
    )
    if existing:
        return existing
    conversation = Conversation.objects.create(is_group=False)
    conversation.participants.set([user, other])
    return conversation


def create_group_conversation(
    *, name: str, creator: User, member_ids: list[int]
) -> Conversation:
    conversation = Conversation.objects.create(
        is_group=True, name=name, created_by=creator
    )
    conversation.participants.add(creator, *User.objects.filter(id__in=member_ids))
    conversation.admins.add(creator)
    return conversation


def rename_conversation(*, conversation: Conversation, name: str) -> Conversation:
    conversation.name = name
    conversation.save(update_fields=["name"])
    return conversation


def add_members(*, conversation: Conversation, user_ids: list[int]) -> Conversation:
    conversation.participants.add(*User.objects.filter(id__in=user_ids))
    return conversation


def remove_member(*, conversation: Conversation, user: User) -> Conversation:
    conversation.participants.remove(user)
    conversation.admins.remove(user)
    return conversation


def leave_conversation(*, conversation: Conversation, user: User) -> None:
    conversation.participants.remove(user)
    conversation.admins.remove(user)


def set_conversation_admin(
    *, conversation: Conversation, user: User, is_admin: bool
) -> Conversation:
    if is_admin:
        conversation.admins.add(user)
    else:
        conversation.admins.remove(user)
    return conversation


def set_admins_only(*, conversation: Conversation, admins_only: bool) -> Conversation:
    conversation.admins_only = admins_only
    conversation.save(update_fields=["admins_only"])
    return conversation


def _assert_can_post(*, conversation: Conversation, sender: User) -> None:
    if (
        conversation.is_group
        and conversation.admins_only
        and not conversation.admins.filter(id=sender.id).exists()
    ):
        raise PermissionDenied("Bu qrupda yalnız adminlər mesaj yaza bilər.")


def edit_message(
    *,
    message: Message,
    editor: User,
    text: str = "",
    ciphertext: str = "",
    nonce: str = "",
) -> Message:
    if message.sender_id != editor.id:
        raise PermissionDenied("Yalnız öz mesajınızı redaktə edə bilərsiniz.")
    if message.attachment:
        raise ValidationError("Qoşması olan mesaj redaktə edilə bilməz.")
    if message.ciphertext:
        if not ciphertext:
            raise ValidationError("ciphertext tələb olunur.")
        message.ciphertext = ciphertext
        message.nonce = nonce
    else:
        if not text.strip():
            raise ValidationError("text boş ola bilməz.")
        message.text = text
    message.edited_at = timezone.now()
    message.save(update_fields=["text", "ciphertext", "nonce", "edited_at"])
    return message


def delete_message(*, message: Message, actor: User) -> None:
    is_group_admin = (
        message.conversation.is_group
        and message.conversation.admins.filter(id=actor.id).exists()
    )
    if message.sender_id != actor.id and not is_group_admin:
        raise PermissionDenied("Bu mesajı silə bilməzsiniz.")
    message.delete()


def send_group_message(
    *, conversation: Conversation, sender: User, text: str, attachment=None
) -> Message:
    _assert_can_post(conversation=conversation, sender=sender)
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        text=text,
        attachment=attachment or "",
    )
    try:
        _notify_participants(
            conversation=conversation,
            sender=sender,
            preview=(
                f"{sender.username}: 📎 Qoşma"
                if attachment
                else f"{sender.username}: {text}"[:200]
            ),
        )
    except Exception:
        pass
    return message


def send_direct_message(
    *,
    conversation: Conversation,
    sender: User,
    ciphertext: str,
    nonce: str,
    attachment=None,
) -> Message:
    # The server never sees plaintext here — `ciphertext`/`nonce` were produced
    # client-side using the recipient's public key. We can't build a content
    # preview for the push notification because we're unable to decrypt it.
    _assert_can_post(conversation=conversation, sender=sender)
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        ciphertext=ciphertext,
        nonce=nonce,
        attachment=attachment or "",
    )
    try:
        _notify_participants(
            conversation=conversation, sender=sender, preview="Yeni mesaj"
        )
    except Exception:
        pass
    return message


def _notify_participants(
    *, conversation: Conversation, sender: User, preview: str
) -> None:
    from apps.notifications.services import send_push_to_users

    recipient_ids = list(
        conversation.participants.exclude(id=sender.id).values_list("id", flat=True)
    )
    if not recipient_ids:
        return
    title = conversation.name if conversation.is_group else sender.username
    send_push_to_users(
        user_ids=recipient_ids,
        title=title,
        body=preview,
        data={"conversation_id": conversation.id},
    )


def list_conversations_for_user(*, user: User):
    # Bring conversations with the most recent activity to the top, WhatsApp-style,
    # falling back to creation time for conversations with no messages yet.
    return (
        Conversation.objects.filter(participants=user)
        .annotate(last_activity=Coalesce(Max("messages__created_at"), "created_at"))
        .order_by("-last_activity")
    )


def mark_conversation_read(*, conversation: Conversation, user: User) -> None:
    now = timezone.now()
    ReadMarker.objects.update_or_create(
        conversation=conversation,
        user=user,
        defaults={"last_read_at": now, "last_delivered_at": now},
    )


def mark_conversations_delivered(*, conversations, user: User) -> None:
    """The user's device just fetched these conversations, so every message
    sent so far has been delivered to them."""
    now = timezone.now()
    for conversation in conversations:
        ReadMarker.objects.update_or_create(
            conversation=conversation,
            user=user,
            defaults={"last_delivered_at": now},
        )


def list_messages(*, conversation: Conversation, after_id: int | None = None):
    qs = conversation.messages.select_related("sender")
    if after_id:
        qs = qs.filter(id__gt=after_id)
    return qs
