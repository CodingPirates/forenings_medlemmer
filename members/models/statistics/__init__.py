from .department_statistic import DepartmentStatistics
from django.utils import timezone


def gatherDayliStatistics():
    timestamp = timezone.now()
    DepartmentStatistics.gatherStatistics(timestamp)
