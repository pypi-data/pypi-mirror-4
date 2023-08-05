from distutils.core import setup

long_description = open('README.rst').read()

setup(
    name='django-markitup-field',
    version="1.2.2-dev",
    package_dir={'markitup_field': 'markitup_field'},
#    packages=['markitup_field', 'markitup_field.tests'],
    packages=['markitup_field'],
    py_modules=['markitup_field'],
    description='Custom Django field for easy use of markup in text fields',
    author='James Turk',
    author_email='james.p.turk@gmail.com',
    license='BSD License',
    url='http://github.com/dimka665/django-markitup-field/',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)