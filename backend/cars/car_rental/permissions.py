from django.db import models
from rest_framework import permissions


class RightsSupport(models.Model):

    class Meta:
        managed = False
        permissions = (
            ('client', 'clients_permission'),
            ('employee', 'employee_permission'),
        )


class ClientFullPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('car_rental.client'):
            return True


class ClientGetPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.has_perm('car_rental.client'):
            return True
        else:
            return False


class EmployeeFullPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('car_rental.employee'):
            return True


class EmployeeGetPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.has_perm('car_rental.employee'):
            return True
        else:
            return False
