from distutils.core import setup
import sms

setup(
    name = "django-sms-gateway",
    version = sms.__version__,
    description = "django generic sms through http gateway",
    long_description = open('README.rst').read(),
    url = "http://bitbucket.org/schinckel/django-sms-gateway",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "sms",
        "sms.migrations",
        "sms.models",
    ],
    package_data = {
        "": [
            "fixtures/*",
            "VERSION",
        ]
    },
    install_requires = [
        'django-jsonfield',
        'django-uuidfield-2',
        'django-picklefield',
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications',
    ],
)
