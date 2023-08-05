# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


package_data = {
    'common': [
        'templates/*.html',
        'templates/base/*.html',
        'templates/email/*.html',
        'templates/forms/*.html',
        'templates/pagination/*.html',
        'static/bootstrap/css/*.css',
        'static/bootstrap/img/*.png',
        'static/bootstrap/js/*.js',
        'static/css/style.css',
        'static/images/*.png',
        'static/js/*.js',
    ]
}
packages = ['common', 'common/templatetags']

setup(
    # Basic package information:
    name = 'zero-common',
    version = '0.1.7',
    author = 'Jose Maria Zambrana Arze',
    author_email = 'contact@josezambrana.com',
    license = 'apache license v2.0',
    url = 'http://github.com/mandlaweb/Zero-Common',
    keywords = 'zero common app',
    description = 'App with common views, libs and templates that can be used by other apps',

    # Packaging options:
    packages = find_packages(),
    package_data = package_data,
    #zip_safe = False,
    #include_package_data = True,

    # Package dependencies:
    install_requires = ['Django>=1.3.1', 'South>=0.7.3', 'django-less>=0.3'],
)
