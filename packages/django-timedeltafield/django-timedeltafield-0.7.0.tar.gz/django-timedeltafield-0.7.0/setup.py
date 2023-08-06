from distutils.core import setup
from timedelta import __version__

setup(
    name = "django-timedeltafield",
    version = __version__,
    description = "TimedeltaField for django models",
    long_description = open("README").read(),
    url = "http://hg.schinckel.net/django-timedelta-field/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "timedelta",
        "timedelta.templatetags",
    ],
    package_data = {'timedelta': ['VERSION']},
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
