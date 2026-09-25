from .models import User


def create_user(
    *,
    username: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    degree: int = 1
) -> User:
    user = User(
        username=username, first_name=first_name, last_name=last_name, degree=degree
    )
    user.set_password(password)
    user.save()
    return user


def search_users(*, query: str, exclude: User):
    qs = User.objects.select_related("section__unit").exclude(id=exclude.id)
    if query:
        qs = qs.filter(username__icontains=query)
    return qs.order_by("username")[:30]


def list_all_users():
    return User.objects.select_related("section__unit").order_by("username")


def set_user_degree(*, user: User, degree: int) -> User:
    user.degree = degree
    user.save(update_fields=["degree"])
    return user


def set_user_public_key(*, user: User, public_key: str) -> User:
    user.public_key = public_key
    user.save(update_fields=["public_key"])
    return user
