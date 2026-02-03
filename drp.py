from rest_framework import fields


class UniversalDRYPermissionField(fields.Field):
    """
    Универсальный класс для DRY permissions
    Наследуется от fields.Field как и DRYPermissionField
    """

    def __init__(self, **kwargs):
        # Устанавливаем read_only=True, так как это поле только для чтения
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        # Возвращаем сам объект, чтобы использовать его в to_representation
        return instance

    def to_representation(self, obj):
        request = self.context.get('request')

        if not request or not hasattr(request, 'user'):
            return {}

        # Определяем модель из сериализатора или объекта
        if hasattr(self.parent, 'Meta') and hasattr(self.parent.Meta, 'model'):
            model = self.parent.Meta.model
        elif obj:
            model = type(obj)
        else:
            return {}

        permissions = {}

        # Стандартные названия permissions как в DRYPermissionField
        permission_pairs = [
            ('read', 'has_read_permission', 'has_object_read_permission'),
            ('write', 'has_write_permission', 'has_object_write_permission'),
            ('create', 'has_create_permission', None),  # create обычно без object-level
            ('update', 'has_update_permission', 'has_object_update_permission'),
            ('partial_update', 'has_partial_update_permission', 'has_object_partial_update_permission'),
            ('destroy', 'has_destroy_permission', 'has_object_destroy_permission'),
            ('delete', 'has_delete_permission', 'has_object_delete_permission'),
            ('list', 'has_list_permission', None),  # list обычно без object-level
            ('retrieve', 'has_retrieve_permission', 'has_object_retrieve_permission'),
        ]

        for perm_name, global_method_name, object_method_name in permission_pairs:
            has_perm = False

            # Проверяем глобальные permissions
            if hasattr(model, global_method_name):
                global_method = getattr(model, global_method_name)
                if callable(global_method):
                    try:
                        has_perm = global_method(request)
                    except (TypeError, ValueError):
                        has_perm = False

            # Проверяем object-level permissions если есть объект и метод
            if obj and object_method_name:
                # Сначала проверяем у объекта
                if hasattr(obj, object_method_name):
                    object_method = getattr(obj, object_method_name)
                    if callable(object_method):
                        try:
                            has_perm = object_method(request)
                        except (TypeError, ValueError):
                            pass
                # Затем проверяем у модели (статический метод с параметром объекта)
                elif hasattr(model, object_method_name):
                    model_object_method = getattr(model, object_method_name)
                    if callable(model_object_method):
                        try:
                            has_perm = model_object_method(request, obj)
                        except (TypeError, ValueError):
                            pass

            permissions[perm_name] = has_perm

        return permissions

    def to_internal_value(self, data):
        # Это read-only поле, не используется для записи
        raise serializers.ValidationError("Permissions field is read-only")