from distutils.core import setup
import os

long_description = open('README.rst').read()

def _static_files(prefix):
    return [os.path.join(prefix, pattern) for pattern in [
        'markitup/*.*',
        'markitup/sets/*.*',
        'markitup/sets/*/*.*',
        'markitup/sets/*/images/*.png',
        'markitup/skins/*/*.*',
        'markitup/skins/*/images/*.png',
        'markitup/templates/*.*'
    ]]

setup(
    name='django-markitup-field',
    version="1.2.10",
    description='Custom Django field for easy use of markup in text fields',
    long_description=long_description,
    author='Dmitry Voronin',
    author_email='dimka665@gmail.com',
    license='BSD License',
    url='http://github.com/dimka665/django-markitup-field/',
    packages=['markitup_field',
              'markitup_field.management', 'markitup_field.management.commands',
              'markitup_field.templatetags',
              'markitup_field.tests',
              ],
    package_data={'markitup_field': ['templates/markitup/*.html'] + _static_files('static')},

    platforms=["any"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Framework :: Django',
        ],
)

