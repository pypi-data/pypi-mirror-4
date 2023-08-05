from django.contrib.auth.models import User
from django.db.models import get_model
from django.utils import timezone

HOUR_DELTA = timezone.timedelta(minutes=60)
MONTH_DELTA = timezone.timedelta(days=30)


class ModelDoesNotExist(Exception):
    pass


class ModelKlass(object):

    def __init__(self, app_model, created=None, modified=None):
        """
            app_model is the app.model we are trying to represent. Examples:

                * auth.User
                * blog.Entry

            created is the name of the field for when something was added to the table
            
            modified is the name of the field for when something was added on a table
            
        """

        try:
            self.app_name, self.model_name = app_model.split('.')
        except IndexError:
            raise ModelDoesNotExist("{0} is an invalid 'app.model'.".format(app_model))

        self.model = get_model(self.app_name, self.model_name)
        if self.model is None:
            raise ModelDoesNotExist("{0} is an invalid 'app.model'.".format(app_model))
            
        if created is None:
            if isinstance(self.model, User):
                self.created = "date_joined"
            else:
                # For use with django_extensions.TimeStampedModel or other defaults
                for field in self.model._meta.fields: 
                    if field.attname == "created":
                        self.created = "created"
                        break
                else:
                    self.created = None

        if modified is None:
            if isinstance(self.model, User):
                self.modified = "last_login"
            else:
                # For use with django_extensions.TimeStampedModel or other defaults
                for field in self.model._meta.fields: 
                    if field.attname == "modified":
                        self.modified = "modified"
                        break
                else:
                    self.modified = None

        self.app_model = app_model
        self.objects = self.model.objects
        self.verbose_name_plural = self.model._meta.verbose_name_plural
        self.verbose_name = self.model._meta.verbose_name
        self.db_table = self.model._meta.db_table
        self.now = timezone.now()
        
    def __repr__(self):
        return "<djangolytics.models.ModelKlass for {0}>".format(self.app_model)

    def count_by_choices(self, field):
        data = {"field_name": field.name, 'counts': []}
        for choice, name in field.choices:
            element = {"name": name}
            element['count'] = self.objects.filter(**{field.name: choice}).count()
            data['counts'].append(element)
        return data

    def query_choices(self):
        result = []
        # do count by choices as a default
        for field in self.model._meta.fields:
            if len(field.choices):
                result.append(self.count_by_choices(field))
        return result

    def construct_date_count_query(self, period, date_control):
        """ period needs to be day, week, month 
            date_control must be either the self.created or self.modified attribute.
            
            TODO - totally refactor this.
        """
        
        # used for custom queries
        date_control__gt = "{0}__gt".format(date_control)
        date_control__lt = "{0}__lt".format(date_control)
        date_control__range = "{0}__range".format(date_control)
        date_control__month = "{0}__month".format(date_control)
        date_control__year = "{0}__year".format(date_control)
        date_control__day = "{0}__day".format(date_control)
        
        if period == "day":
            try:
                # can't rely on latest field being defined
                date = self.model.objects.dates(date_control, 'day', 'DESC')[0]
            except IndexError:
                # If no records, table is empty so we return a zilch query
                return []
            
            # update base_date if it matches today. This way we get more accurate queries
            if date.date() == self.now.date():
                date = self.now
            
            # Make a range of hours for the chart
            hours = [date - (HOUR_DELTA * x) for x in range(24)]

            # Do 24 hours of count queries, 1 for each hour
            return [
                {'hour':i, 'date':x.isoformat(), 'count':self.model.objects.filter(
                        **{date_control__gt: x, date_control__lt: x + HOUR_DELTA}
                    ).count()
                } for i,x in enumerate(hours)
            ]

        if period == "month":
            # get records for past 30 days
            start_date = self.now - MONTH_DELTA
            dates = self.model.objects.filter(**{date_control__range:(start_date, self.now)})
            # now get the distinct date values
            dates = dates.dates(date_control, 'day', 'DESC')
            
            # Do 30 days of count queries
            return [
                {'day':i, 'date':x.isoformat(), 'count':self.model.objects.filter(**{
                        date_control__month:x.month,
                        date_control__year:x.year,
                        date_control__day:x.day,
                        }
                    ).count()
                } for i,x in enumerate(dates)
            ]
        return "BLARG"


    def query_created(self):
        if self.created is None:
            return {}
        result = {}
        # day: last 24 hours
        result["day"] = self.construct_date_count_query("day", self.created)
                
        # months: 30 days
        result["month"] = self.construct_date_count_query("month", self.created)
        return result

    def query_modified(self):
        if self.modified is None:
            return {}
        result = {}
        # day: last 24 hours
        result["day"] = self.construct_date_count_query("day", self.modified)
                
        # months: 30 days
        result["month"] = self.construct_date_count_query("month", self.modified)
        return result
