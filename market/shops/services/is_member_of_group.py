from django.contrib.auth.models import Group


def is_member_of_group(group_name):
    """Проверка на принадлежность пользователя к группе"""

    def check(user):
        try:
            group = Group.objects.get(name=group_name)
            return group in user.groups.all()
        except Group.DoesNotExist:
            pass

    return check
