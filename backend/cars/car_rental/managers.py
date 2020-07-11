from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import Permission
from .permissions import RightsSupport


class ClientManager(models.Manager):
    def create_client(self, user):
        client = self.create(user=user)
        content_type = ContentType.objects.get_for_model(RightsSupport)
        client_perm = Permission.objects.get(
            content_type=content_type,
            codename='client'
        )
        user.user_permissions.add(client_perm)
        return client
