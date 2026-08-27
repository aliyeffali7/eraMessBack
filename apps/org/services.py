from apps.accounts.models import User
from apps.chat.models import Conversation

from .models import Section, Unit


def create_unit(*, name: str, creator: User) -> Unit:
    conversation = Conversation.objects.create(is_group=True, name=name, created_by=creator)
    conversation.participants.add(creator)
    conversation.admins.add(creator)
    return Unit.objects.create(name=name, conversation=conversation, created_by=creator)


def create_section(*, unit: Unit, name: str, creator: User) -> Section:
    conversation = Conversation.objects.create(
        is_group=True, name=f"{unit.name} / {name}", created_by=creator
    )
    conversation.participants.add(creator)
    conversation.admins.add(creator)
    return Section.objects.create(unit=unit, name=name, conversation=conversation, created_by=creator)


def assign_user_to_section(*, user: User, section: Section) -> User:
    user.section = section
    user.save(update_fields=["section"])
    section.conversation.participants.add(user)
    section.unit.conversation.participants.add(user)
    return user


def list_units():
    return Unit.objects.prefetch_related("sections").all()


def rename_unit(*, unit: Unit, name: str) -> Unit:
    unit.name = name
    unit.save(update_fields=["name"])
    unit.conversation.name = name
    unit.conversation.save(update_fields=["name"])
    return unit


def rename_section(*, section: Section, name: str) -> Section:
    section.name = name
    section.save(update_fields=["name"])
    section.conversation.name = f"{section.unit.name} / {name}"
    section.conversation.save(update_fields=["name"])
    return section
