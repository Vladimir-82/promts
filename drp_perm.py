from rest_framework import permissions


class SimpleDRYPermission(permissions.BasePermission):
    """
    Простая версия DRY permissions
    """

    def has_permission(self, request, view):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return self._check_global_permission(request, view, 'read')
        else:
            if view.action == 'create':
                return self._check_global_permission(request, view, 'create')
            return self._check_global_permission(request, view, 'write')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return self._check_object_permission(request, obj, 'read')
        elif request.method in ['PUT', 'PATCH']:
            return self._check_object_permission(request, obj, 'write')
        elif request.method == 'DELETE':
            return self._check_object_permission(request, obj, 'destroy')
        return False

    def _check_global_permission(self, request, view, perm_type):
        """Проверка глобальных permissions"""
        model = getattr(view, 'queryset', None)
        if model:
            model = model.model

        if not model:
            return False

        method_name = f'has_{perm_type}_permission'

        if hasattr(model, method_name) and callable(getattr(model, method_name)):
            return getattr(model, method_name)(request)

        # Дефолтные значения
        if perm_type == 'read':
            return True
        return request.user and request.user.is_authenticated

    def _check_object_permission(self, request, obj, perm_type):
        """Проверка object-level permissions"""
        method_name = f'has_object_{perm_type}_permission'

        if hasattr(obj, method_name) and callable(getattr(obj, method_name)):
            return getattr(obj, method_name)(request)

        # Дефолтные значения
        if perm_type == 'read':
            return True
        return False