from django.db.models import Subquery, OuterRef, FloatField, F, Q, Value
from django.db.models.functions import Coalesce, Abs
from datetime import date


def get_clients_orm_with_changes():
    date1 = date(2025, 7, 1)
    date2 = date(2025, 10, 1)

    # Субзапросы для балансов на первую дату
    subquery_date1 = Balance.objects.filter(
        client_id=OuterRef('pk'),  # OuterRef ссылается на Client
        date=date1
    ).values('b110', 'b120')[:1]

    # Субзапросы для балансов на вторую дату
    subquery_date2 = Balance.objects.filter(
        client_id=OuterRef('pk'),
        date=date2
    ).values('b110', 'b120')[:1]

    # Получаем клиентов, у которых есть балансы на обе даты
    clients = Client.objects.filter(
        # Проверяем, что есть баланс на первую дату
        balance__date=date1
    ).filter(
        # И есть баланс на вторую дату
        balance__date=date2
    ).distinct().annotate(
        # Аннотируем значения с первой даты
        b110_date1=Coalesce(
            Subquery(subquery_date1.values('b110')),
            Value(0),
            output_field=FloatField()
        ),
        b120_date1=Coalesce(
            Subquery(subquery_date1.values('b120')),
            Value(0),
            output_field=FloatField()
        ),
        # Аннотируем значения со второй даты
        b110_date2=Coalesce(
            Subquery(subquery_date2.values('b110')),
            Value(0),
            output_field=FloatField()
        ),
        b120_date2=Coalesce(
            Subquery(subquery_date2.values('b120')),
            Value(0),
            output_field=FloatField()
        ),
        # Вычисляем абсолютные разницы
        abs_diff_b110=Abs(F('b110_date2') - F('b110_date1')),
        abs_diff_b120=Abs(F('b120_date2') - F('b120_date1'))
    ).filter(
        # Фильтруем по пороговому значению
        Q(abs_diff_b110__gt=10000) | Q(abs_diff_b120__gt=10000)
    ).values(
        'id', 'name', 'email',  # Поля клиента
        'b110_date1', 'b120_date1',
        'b110_date2', 'b120_date2',
        'abs_diff_b110', 'abs_diff_b120'
    )

    return clients