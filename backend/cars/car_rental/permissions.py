from django.db import models


class RightsSupport(models.Model):

    class Meta:
        managed = False
        permissions = (
            ('client', 'clients_permission'),
        )
