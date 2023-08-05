Django is a high-level Python Web framework that encourages rapid development
and clean, pragmatic design. This fork (pkg name Django-ArrayAccum on pypi) allows you to use the array_accum function available in Postgresql. This function will *NOT* work in other databases. If you are happy with Postgresql and want to be able to use the array_accum within Django (and not write custom sql) this fork is for you to try.

This fork was created from Django-1.5 dev version from the master branch. Will try to keep it up-to-date with django master. Feel free to remind me if it gets behind.

This fork just modifies two files.

1) django/db/models/aggregates.py
2) django/db/models/sql/aggregates.py

This adds a function called ArrayAccum which you can then use in any query involving aggregations (similar to Sum, Avg etc which are built-in).

Example Usage:
Suppose you have a model defined as such::

    class People(models.Model):
        first_name = models.CharField(max_length=100)
        last_name = models.CharField(max_length=100)

And lets say you want to show the most common last names, count, associated first names --- then here is how you can do it::

    from django.db.models import Count, ArrayAccum
    results = People.objects.values("last_name").annotate(count=Count('id'),
                            unique_first_names=ArrayAccum("first_name", distinct=True)).order_by('-count')

Everything else is standard Django stuff version 1.5+. Django documentation is in the "docs" directory and online at http://docs.djangoproject.com/en/dev/.

GitHub: http://github.com/wisedragon/django

PyPi: http://pypi.python.org/pypi/Django-ArrayAccum/
