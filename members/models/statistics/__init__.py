from .department_statistic import DepartmentStatistics
from django.utils import timezone

from .old_stat_code import old_stat_code


def gatherDayliStatistics():
    # TODO add other models here
    current_time = timezone.now()

    # Check if it has all readey been run
    all_stats = DepartmentStatistics.objects.all().order_by("-timestamp")
    newest_stat = all_stats[1] if len(all_stats) > 1 else None
    if newest_stat is None or newest_stat.timestamp.date() < current_time.date():
        DepartmentStatistics.gatherStatistics(current_time)
        old_stat_code(current_time)
