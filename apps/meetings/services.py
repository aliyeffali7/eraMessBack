from django.utils import timezone

from apps.accounts.models import User

from .models import Meeting, MeetingInvite


def resolve_target_user_ids(
    *, user_ids=None, section_ids=None, unit_ids=None, all_users=False
) -> set[int]:
    if all_users:
        return set(User.objects.filter(is_active=True).values_list("id", flat=True))
    ids = set(user_ids or [])
    if section_ids:
        ids.update(
            User.objects.filter(section_id__in=section_ids).values_list("id", flat=True)
        )
    if unit_ids:
        ids.update(
            User.objects.filter(section__unit_id__in=unit_ids).values_list(
                "id", flat=True
            )
        )
    return ids


def create_meeting(
    *,
    title: str,
    description: str,
    location: str,
    starts_at,
    ends_at,
    creator: User,
    user_ids=None,
    section_ids=None,
    unit_ids=None,
    all_users=False,
) -> Meeting:
    meeting = Meeting.objects.create(
        title=title,
        description=description,
        location=location,
        starts_at=starts_at,
        ends_at=ends_at,
        created_by=creator,
    )
    target_ids = resolve_target_user_ids(
        user_ids=user_ids,
        section_ids=section_ids,
        unit_ids=unit_ids,
        all_users=all_users,
    )
    target_ids.add(creator.id)
    MeetingInvite.objects.bulk_create(
        [MeetingInvite(meeting=meeting, user_id=uid) for uid in target_ids]
    )
    try:
        _notify_invitees(meeting=meeting, target_ids=target_ids, creator=creator)
    except Exception:
        pass
    return meeting


def _notify_invitees(*, meeting: Meeting, target_ids: set[int], creator: User) -> None:
    from apps.notifications.services import send_push_to_users

    recipient_ids = [uid for uid in target_ids if uid != creator.id]
    if not recipient_ids:
        return
    when = timezone.localtime(meeting.starts_at).strftime("%d.%m.%Y %H:%M")
    send_push_to_users(
        user_ids=recipient_ids,
        title="Yeni iclas",
        body=f"{meeting.title} — {when}",
        data={"meeting_id": meeting.id, "type": "meeting"},
    )


def respond_to_meeting(
    *, meeting: Meeting, user: User, response: str, reason: str = ""
) -> MeetingInvite | None:
    invite = MeetingInvite.objects.filter(meeting=meeting, user=user).first()
    if invite is None:
        return None
    invite.response = response
    invite.reason = reason.strip() if response == MeetingInvite.NO else ""
    invite.save(update_fields=["response", "reason"])
    if response == MeetingInvite.NO and meeting.created_by_id not in (None, user.id):
        try:
            _notify_decline(meeting=meeting, user=user, reason=invite.reason)
        except Exception:
            pass
    return invite


def _notify_decline(*, meeting: Meeting, user: User, reason: str) -> None:
    from apps.notifications.services import send_push_to_users

    name = f"{user.first_name} {user.last_name}".strip() or user.username
    body = f"{name} gələ bilmir" + (f": {reason}" if reason else "")
    send_push_to_users(
        user_ids=[meeting.created_by_id],
        title=meeting.title,
        body=body[:200],
        data={"meeting_id": meeting.id, "type": "meeting_decline"},
    )


def list_meetings_for_user(*, user: User):
    return Meeting.objects.filter(invites__user=user).order_by("starts_at")


def list_all_meetings():
    return Meeting.objects.order_by("starts_at")
