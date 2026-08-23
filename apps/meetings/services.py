from apps.accounts.models import User

from .models import Meeting, MeetingInvite


def resolve_target_user_ids(*, user_ids=None, section_ids=None, unit_ids=None) -> set[int]:
    ids = set(user_ids or [])
    if section_ids:
        ids.update(User.objects.filter(section_id__in=section_ids).values_list("id", flat=True))
    if unit_ids:
        ids.update(User.objects.filter(section__unit_id__in=unit_ids).values_list("id", flat=True))
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
) -> Meeting:
    meeting = Meeting.objects.create(
        title=title,
        description=description,
        location=location,
        starts_at=starts_at,
        ends_at=ends_at,
        created_by=creator,
    )
    target_ids = resolve_target_user_ids(user_ids=user_ids, section_ids=section_ids, unit_ids=unit_ids)
    target_ids.add(creator.id)
    MeetingInvite.objects.bulk_create([MeetingInvite(meeting=meeting, user_id=uid) for uid in target_ids])
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
    send_push_to_users(
        user_ids=recipient_ids,
        title="Yeni iclas",
        body=meeting.title,
        data={"meeting_id": meeting.id},
    )


def respond_to_meeting(*, meeting: Meeting, user: User, response: str) -> MeetingInvite | None:
    invite = MeetingInvite.objects.filter(meeting=meeting, user=user).first()
    if invite is None:
        return None
    invite.response = response
    invite.save(update_fields=["response"])
    return invite


def list_meetings_for_user(*, user: User):
    return Meeting.objects.filter(invites__user=user).order_by("starts_at")


def list_all_meetings():
    return Meeting.objects.order_by("starts_at")
