=============================
django-admin-tools-user-stats
=============================

This app provides django-admin-tools dashboard modules with user
registration stats/charts.

The license is MIT.

Installation
============

Make sure django-admin-tools >= 0.4.0 is installed and then

::

    pip install "django-qsstats-magic >= 0.6.1"
    pip install "python-dateutil==1.5"
    pip install "django-chart-tools >= 0.2.1"
    pip install django-admin-user-stats

Then add 'admin_user_stats' and 'chart_tools' to INSTALLED_APPS.

Quickstart
==========

Import ``RegistrationCharts`` dashboard module::

    from admin_user_stats.modules import RegistrationCharts

then and add it to dashboard's children::

    self.children += [RegistrationCharts()]

go to admin and enjoy the result_.

.. _result: https://bitbucket.org/kmike/django-admin-user-stats/downloads/RegistrationCharts.png

Usage
=====

RegistrationChart
-----------------

Dashboard module with user registration charts (new users per day,
week or month).

To enable, import it::

    from admin_user_stats.modules import RegistrationChart

and add to dashboard's children (or to modules.Group)::

    self.children += [RegistrationChart('New Users', interval='days', days=30)]


RegistrationCharts
------------------

Group subclass with 3 default children modules (new users per day,
per week and per month).


Advanced Usage
=============

New BaseChart(s) abstract modules are there for you to play with.  Want to track kitten activity?

BaseChart
---------

To build charts for other time-series data, inherit from BaseChart and set a few attributes::

    from admin_user_stats.base_modules import BaseChart
    from kitten.models import Activity


    class ActivityChart(BaseChart):
        """
        Dashboard module with Activity charts.
        """
        title = _('How Active were the kittens')
        template = 'admin_user_stats/modules/chart.html'
        chart_size = "580x100"
        days = None
        interval = 'days'
        queryset = Activity.objects.filter(kitten=True).exclude(active=None)
        date_field = 'activity_date'

BaseCharts
---------

To collect those charts in to the normal Day,Week,Month tabs::

    from admin_user_stats.base_modules import BaseChart


    class ApplicationCharts(BaseCharts):
        """ Group module with 3 default registration charts """
        title = _('Kitten Activity')
        chart_model = ActivityChart

Contributing
============

Development of django-admin-user-stats happens at Bitbucket and Github:

* https://bitbucket.org/kmike/django-admin-user-stats
* https://github.com/kmike/django-admin-user-stats

If you don’t like Bitbucket, Github, Mercurial and Git you’re welcome
to send regular patches.

Bug tracker: https://github.com/kmike/django-admin-user-stats/issues
