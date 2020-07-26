import os
import environ
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import Permission
from cars import settings
from .permissions import RightsSupport


class ClientManager(models.Manager):
    env = environ.Env()
    env.read_env('../cars/.env')
    empty_avatar = env('EMPTY_AVATAR')  # default-img location in AWS bucket

    def create_client(self, user, avatar):
        if avatar is None:
            path = self.empty_avatar
            client = self.create(user=user, avatar=path)
        else:
            client = self.create(user=user, avatar=avatar)

        content_type = ContentType.objects.get_for_model(RightsSupport)
        client_perm = Permission.objects.get(
            content_type=content_type,
            codename='client'
        )
        user.user_permissions.add(client_perm)

        return client
