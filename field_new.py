from rest_framework import fields


class DRYPermissionsField(fields.Field):
    """
    Простой аналог DRYPermissionsField из dry_rest_permissions.
    Наследуется от fields.Field как в оригинальной библиотеке.

    Использование:
        from rest_framework import serializers

        class MySerializer(serializers.ModelSerializer):
            permissions = DRYPermissionsField()
    """

    def __init__(self, **kwargs):
        """
        Инициализация. Поле всегда только для чтения.
        """
        # В оригинале тоже read_only=True по умолчанию
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        """
        Вычисляет и возвращает права доступа для текущего объекта.

        Args:
            value: Обычно игнорируется, объект берется из parent.instance

        Returns:
            dict: Словарь прав доступа
        """
        # 1. Получаем текущий объект из родительского сериализатора
        obj = self.parent.instance

        # 2. Получаем request из контекста
        request = None
        if hasattr(self, '_context'):
            request = self._context.get('request')

        # 3. Базовые проверки
        if not request or not obj:
            return {}

        user = request.user
        if not user or not user.is_authenticated:
            return {}

        # 4. Получаем view для дополнительного контекста
        view = self._context.get('view') if hasattr(self, '_context') else None

        # 5. Вычисляем права
        return self._get_permissions(obj, user, view, request)

    def _get_permissions(self, obj, user, view, request):
        """
        Основная логика вычисления прав.
        Может быть переопределена в подклассах.

        Args:
            obj: Объект для проверки прав
            user: Текущий пользователь
            view: Текущее представление (view)
            request: HTTP запрос

        Returns:
            dict: Словарь с правами
        """
        permissions = {}

        # Проверка стандартных Django permissions
        if hasattr(obj, '_meta'):
            app_label = obj._meta.app_label
            model_name = obj._meta.model_name

            # Базовые CRUD права
            permissions.update({
                'can_view': user.has_perm(f'{app_label}.view_{model_name}', obj),
                'can_edit': user.has_perm(f'{app_label}.change_{model_name}', obj),
                'can_delete': user.has_perm(f'{app_label}.delete_{model_name}', obj),
                'can_create': user.has_perm(f'{app_label}.add_{model_name}'),
            })

        # Проверка владения объектом
        if hasattr(obj, 'owner'):
            is_owner = obj.owner == user
            permissions.update({
                'is_owner': is_owner,
                'can_edit': permissions.get('can_edit', False) or is_owner,
                'can_delete': permissions.get('can_delete', False) or is_owner,
            })

        # Проверка по группам пользователей
        if hasattr(obj, 'group'):
            if hasattr(user, 'groups'):
                user_groups = user.groups.all()
                permissions['in_group'] = obj.group in user_groups

        # Дополнительные кастомные проверки
        if view and hasattr(view, 'action'):
            action = view.action
            permissions['current_action'] = action

            # Для разных действий могут быть разные права
            if action in ['update', 'partial_update']:
                permissions['allowed'] = permissions.get('can_edit', False)
            elif action == 'destroy':
                permissions['allowed'] = permissions.get('can_delete', False)

        return permissions

    def to_internal_value(self, data):
        """
        Преобразование входящих данных.
        Так как поле только для чтения, всегда выбрасывает ошибку.

        Args:
            data: Входящие данные

        Raises:
            ValidationError: Всегда, так как поле read-only
        """
        raise fields.ValidationError({
            self.field_name: 'Это поле доступно только для чтения.'
        })

    def get_attribute(self, instance):
        """
        Получает атрибут для сериализации.

        Args:
            instance: Экземпляр модели

        Returns:
            Сам экземпляр, так как права вычисляются на его основе
        """
        return instance

    def bind(self, field_name, parent):
        """
        Привязка поля к родительскому сериализатору.
        Вызывается автоматически DRF.

        Args:
            field_name: Имя поля
            parent: Родительский сериализатор
        """
        super().bind(field_name, parent)

        # Сохраняем ссылку на родительский сериализатор
        # для доступа к instance и context
        self.parent = parent
        if hasattr(parent, '_context'):
            self._context = parent._context


# Минималистичная версия, максимально приближенная к оригиналу
class SimpleDRYPermissionsField(fields.Field):
    """
    Минималистичная реализация, максимально похожая на оригинал.
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        # Минимальная необходимая логика
        try:
            obj = self.parent.instance
            request = self.parent.context.get('request')

            if not request or not request.user.is_authenticated or not obj:
                return {}

            user = request.user

            # Базовая проверка прав
            perms = {}
            if hasattr(obj, '_meta'):
                app = obj._meta.app_label
                model = obj._meta.model_name

                perms = {
                    'view': user.has_perm(f'{app}.view_{model}', obj),
                    'change': user.has_perm(f'{app}.change_{model}', obj),
                    'delete': user.has_perm(f'{app}.delete_{model}', obj),
                }

            return perms

        except (AttributeError, KeyError):
            return {}

    def to_internal_value(self, data):
        raise fields.ValidationError("Read only field")

    def get_attribute(self, instance):
        return instance


# Пример использования в проекте
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    permissions = DRYPermissionsField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'permissions']


# Кастомная реализация для конкретной модели
class ArticlePermissionsField(DRYPermissionsField):
    """Права доступа для статей"""

    def _get_permissions(self, obj, user, view, request):
        # Сначала получаем базовые права
        perms = super()._get_permissions(obj, user, view, request)

        # Специфичные для статьи проверки
        if hasattr(obj, 'author'):
            is_author = obj.author == user
            perms.update({
                'is_author': is_author,
                'can_publish': is_author or user.has_perm('articles.publish_article'),
                'can_comment': user.is_authenticated,
                'can_like': user.is_authenticated,
            })

        # Проверка статуса статьи
        if hasattr(obj, 'status'):
            if obj.status == 'published':
                perms['can_edit'] = False  # Опубликованные нельзя редактировать
            elif obj.status == 'draft':
                perms['can_view'] = perms.get('is_author', False)  # Черновики видят только авторы

        return perms


# Сериализатор с кастомными правами
class ArticleSerializer(serializers.ModelSerializer):
    permissions = ArticlePermissionsField()

    class Meta:
        model = Article  # Предполагаем, что есть модель Article
        fields = ['id', 'title', 'content', 'status', 'permissions']