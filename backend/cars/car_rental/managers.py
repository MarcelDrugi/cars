from os.path import abspath, dirname, join

import environ
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .permissions import RightsSupport


class ClientManager(models.Manager):
    env = environ.Env()
    EMPTY_AVATAR = env('EMPTY_AVATAR')  # default-img location in AWS bucket

    def create_client(self, user, avatar):
        if avatar is None:
            path = self.EMPTY_AVATAR
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
