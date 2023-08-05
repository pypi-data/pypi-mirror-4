from distutils.core import setup

setup(
    name='django-related',
    description='Class-based-views mixins for handling related objects',
    long_description=open('README.rst').read(),
    version='0.0.2',
    packages=['related'],
    author='Monwara LLC',
    author_email='branko@monwara.com',
    url='https://bitbucket.org/monwara/django-related',
    download_url='https://bitbucket.org/monwara/django-related/downloads',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
)


