from distutils.core import setup

setup(
    name='django-ga-tracking',
    description='Simple Google Analytics integration for Django projects',
    long_description=open('README.rst').read(),
    version='0.0.1',
    packages=['ga_tracking'],
    package_data={
        'ga_tracking': ['templates/ga_tracking/*.html'],
    },
    include_package_data=True,
    author='Monwara LLC',
    author_email='branko@monwara.com',
    url='https://bitbucket.org/monwara/django-ga-tracking',
    download_url='https://bitbucket.org/monwara/django-ga-tracking/downloads',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
)


