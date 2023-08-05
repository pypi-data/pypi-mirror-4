from distutils.core import setup

setup(
    name='django-autohide-help',
    description='jQuery plugin that auto-hides form field help blocks as '
    'pluggable Django app',
    long_description=open('README.rst').read(),
    version='0.0.1',
    packages=['autohide_help'],
    package_data={
        'autohide_help': ['static/js/*.js'],
    },
    include_package_data=True,
    author='Monwara LLC',
    author_email='branko@monwara.com',
    url='https://bitbucket.org/monwara/django-autohide-help',
    download_url='https://bitbucket.org/monwara/django-autohide-help/downloads',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
)


