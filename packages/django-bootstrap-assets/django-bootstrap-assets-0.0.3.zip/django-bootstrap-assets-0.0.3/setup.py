from distutils.core import setup

setup(
    name='django-bootstrap-assets',
    description='jQuery plugin that auto-hides form field help blocks as '
    'pluggable Django app',
    long_description=open('README.rst').read(),
    version='0.0.3',
    packages=[
        'bootstrap',
        'bootstrap_all',
        'bootstrap_datepicker',
        'bootstrap_select2',
    ],
    package_data={
        'bootstrap': [
            'static/js/*.js',
            'static/css/*.css',
            'static/img/*.png',
        ],
        'bootstrap_all': [
            'static/js/*.js',
            'static/css/*.css',
            'static/img/*.png',
            'static/img/*.gif',
        ],
        'bootstrap_datepicker': [
            'static/js/*.js',
            'static/css/*.css'
        ],
        'bootstrap_select2': [
            'static/js/*.js',
            'static/css/*.css',
            'static/img/*.png',
            'static/img/*.gif',
        ],
    },
    include_package_data=True,
    author='Monwara LLC',
    author_email='branko@monwara.com',
    url='https://bitbucket.org/monwara/django-bootstrap-assets',
    download_url='https://bitbucket.org/monwara/django-bootstrap-assets/downloads',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
)


