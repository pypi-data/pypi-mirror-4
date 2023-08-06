# Todo: Simplify entire presentation layer by making this assume Django. Pylons will not be supported here. Supporting different versions of Django might still be useful.
# Todo: Completely remove all support for Django version < 1.0.
# Todo: Add support for most recent stable version of Django (and development version, to anticipate next stable version).
from dm.exceptions import WebkitError
from dm.dictionarywords import WEBKIT_NAME
from dm.ioc import RequiredFeature

dictionary = RequiredFeature('SystemDictionary')
webkitName = dictionary[WEBKIT_NAME]
webkitVersion = ''  # Inferred version.
webkitVersionFull = ''  # Actual, if available.
if not webkitName:
    pass
elif webkitName == 'django':
    import django
    import django.forms
    if hasattr(django.forms, 'BaseForm'): # Django >= v1.0
        webkitVersion = '1.0'  # ...and up. (Todo: Revisit version detection).
        webkitVersionFull = django.get_version()
        from django.forms.forms import BaseForm
        from django.forms.util import ValidationError
        from django.utils.html import escape as htmlescape
        from django.http import HttpRequest
        from django.http import HttpResponse
        from django.http import HttpResponseBadRequest
        from django.http import HttpResponseNotFound
        from django.http import HttpResponseRedirect
        from django.template import Context
        if webkitVersionFull[1] >= 2:
            from django.template import RequestContext
        else:
            RequestContext = None
        from django.core import template_loader
        from django.forms import Field
        from django.forms import CharField
        from django.forms import RegexField
        from django.forms import BooleanField
        from django.forms import EmailField
        from django.forms import ChoiceField
        from django.forms import MultipleChoiceField
        from django.forms import DateTimeField
        from django.forms import TimeField
        from django.forms import DateField
        from django.forms import IntegerField
        from django.forms import ImageField
        from django.forms import URLField
        from django.forms import widgets
        from django.forms import fields
        from django.utils.datastructures import SortedDict

    else:
        raise Exception, "KForge no longer supports Django versions less than 1.0 "

else:
    raise WebkitError, "No support available for '%s' webkit." % webkitName




DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%d-%m-%Y', '%d-%m-%y', # '2006-10-25', '25-10-2006', '25-10-06'
    '%Y/%m/%d', '%d/%m/%Y', '%d/%m/%y', # '2006/10/25', '25/10/2006', '25/10/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
)

class Manipulator(BaseForm):

    pass


class ManipulatedField(Field):

    def __init__(self, manipulator=None, *args, **kwds):
        self.manipulator = manipulator
        super(ManipulatedField, self).__init__(*args, **kwds)


class DateField(DateField):
    
    def __init__(self, input_formats=None, *args, **kwargs):
        input_formats = input_formats or DATE_INPUT_FORMATS
        super(DateField, self).__init__(input_formats=input_formats, *args, **kwargs)



