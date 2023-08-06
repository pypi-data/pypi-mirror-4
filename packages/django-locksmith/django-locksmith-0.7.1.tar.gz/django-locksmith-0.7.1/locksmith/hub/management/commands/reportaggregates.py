from django.db.models import Min, Max
from django.core.management.base import BaseCommand, CommandError
from locksmith.common import cycle_generator
from locksmith.hub.models import Key, MonthlyReportAggregate

class Command(BaseCommand):
    help = 'Update cached report aggregates.'

    def handle(self, *args, **options):
        if len(args) == 0:
            self.update_for_all()
        else:
            for arg in args:
                try:
                    key = Key.objects.get(key=arg)
                    self.update_for_key(key)
                except Key.DoesNotExist:
                    raise CommandError("No such key: {0}".format(arg))

    def update_for_all(self):
        raise NotImplementedError('update_for_all')

    def update_for_key(self, key):
        agg = key.reports.aggregate(earliest=Min('date'), latest=Max('date'))
        earliest_yrmon = (agg['earliest'].year, agg['earliest'].month)
        latest_yrmon = (agg['latest'].year, agg['latest'].month)

        for (year, month) in cycle_generator(cycle=(1, 12), begin=earliest_yrmon, end=latest_yrmon):
            MonthlyReportAggregate.compute(key, year, month)


