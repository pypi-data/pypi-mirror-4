from django.db.models import Q

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from account.models import EmailAddress


class AnnouncementPermissionsBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = True
    
    def has_perm(self, user, perm, obj=None):
        if perm == "announcements.can_manage":
            return user.is_authenticated() and user.is_staff
        return super(AnnouncementPermissionsBackend, self).has_perm(user, perm)
