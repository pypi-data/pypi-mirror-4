from setuptools import setup, find_packages

setup(
    name = "django_internal_urls",
    version = "0.1.0",
    description = 'Add modular url callbacks',
    author = 'David Danier',
    author_email = 'david.danier@team23.de',
    url = 'https://github.com/ddanier/django_internal_urls',
    #long_description=open('README.rst', 'r').read(),
    packages = [
        'django_internal_urls',
        'django_internal_urls.templatetags',
    ],
    requires = [
        'django(>=1.4)',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)

