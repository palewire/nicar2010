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
        
    def latest(self):
        """
        Return the data for the latest month, which is determined dynamically.
        """
        try:
           # Fetch the most recent month in the database
            latest_month = self.values(
                'year', 'month'
                ).order_by('-year', '-month')[0]
        except IndexError:
            from unemployment.models import CountyByMonth
            # If there aren't any records to pull, throw an error
            raise CountyByMonth.DoesNotExist(
                'The latest CountyByMonth cannot be found.'
                )
        # Query and return all records from the kwargs pulled above
        return self.filter(**latest_month)


