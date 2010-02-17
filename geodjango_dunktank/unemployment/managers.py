from django.contrib.gis.db import models


class SeasonallyAdjustedManager(models.Manager):
    """
    Returns seasonally adjusted unemployment numbers.
    """

    def get_query_set(self):
        qs = super(SeasonallyAdjustedManager, self).get_query_set().filter(
           is_seasonally_adjusted=True
        )
        return qs


class UnadjustedManager(models.Manager):
    """
    Returns unemployment numbers that have not been seasonally adjusted.
    """

    def get_query_set(self):
        qs = super(UnadjustedManager, self).get_query_set().filter(
           is_seasonally_adjusted=False
        )
        return qs


