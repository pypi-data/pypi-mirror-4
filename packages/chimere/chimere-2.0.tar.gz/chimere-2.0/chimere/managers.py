# -*- coding: utf-8 -*-
import sys

from django.contrib.gis.db import models

from logging import getLogger
from datetime import datetime, date, timedelta

from django.conf import settings

# BASE
class BaseGeoQuerySet(models.query.QuerySet):
    """
    Custom queryset for Geo objects.
    """
    def available(self):
        """ Chainable filter to retrieve only available elements. """
        return self.filter(status="A")
    
    def submited(self):
        """ Chainable filter to retrieve only submited elements. """
        return self.filter(status="S")
    
    def active(self):
        """
        Returns objects where within the active date period of events.
        """
        # Fields are not set in the model in this case
        if not settings.CHIMERE_DAYS_BEFORE_EVENT:
            return self
        today = date.today()
        after = today + timedelta(settings.CHIMERE_DAYS_BEFORE_EVENT)
        return self.filter(end_date__gte=today, start_date__lte=after)
    
class BaseGeoManager(models.GeoManager):
    """
    Custom base manager for Geo objects.
    """
    def get_query_set(self):
        """ Use our custom QuerySet. """
        return BaseGeoQuerySet(self.model)
    
    # Methods defined in the queryset that we also want exposed in the
    # It would be nice to implement it with a magic method instead, later :)
    def available(self):
        return self.get_query_set().available()
    
    def submited(self):
        return self.get_query_set().submited()
    
    def active(self):
        return self.get_query_set().active()
