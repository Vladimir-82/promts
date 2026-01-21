from django.db.models import Subquery, OuterRef, FloatField, F, Value
from django.db.models.functions import Coalesce


def get_balances_with_changes_sql():
    date1 = date(2025, 7, 1)
    date2 = date(2025, 10, 1)

    # Субзапрос для первой даты
    subquery_date1 = Balance.objects.filter(
        account_id=OuterRef('account_id'),
        date=date1
    ).values('b110')[:1]

    # Субзапрос для второй даты
    subquery_date2 = Balance.objects.filter(
        account_id=OuterRef('account_id'),
        date=date2
    ).values('b110')[:1]

    # Основной запрос
    balances = Balance.objects.filter(
        Q(date=date1) | Q(date=date2)
    ).values('account_id').annotate(
        b110_date1=Coalesce(
            Subquery(subquery_date1),
            Value(0),
            output_field=FloatField()
        ),
        b110_date2=Coalesce(
            Subquery(subquery_date2),
            Value(0),
            output_field=FloatField()
        ),
        difference=F('b110_date2') - F('b110_date1')
    ).filter(
        difference__abs__gt=10000
    ).distinct()

    return balances