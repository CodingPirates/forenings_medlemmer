from .department_statistic import DepartmentStatistics
from django.utils import timezone


def gatherDayliStatistics():
    # TODO add other models here
    timestamp = timezone.now()
    DepartmentStatistics.gatherStatistics(timestamp)
