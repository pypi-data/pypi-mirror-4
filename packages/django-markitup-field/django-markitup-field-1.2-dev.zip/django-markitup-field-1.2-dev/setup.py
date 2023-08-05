from distutils.core import setup
#import glob
#import os

long_description = open('README.rst').read()

#path = os.path.abspath(os.path.dirname(__file__))
#print(path)
#path = os.path.join(path, 'static/*.*')
#print(path)

#static_files = glob.glob('static/*.*')
#static_files = glob.glob(path)
#print(static_files)

setup(
    name='django-markitup-field',
    version="1.2-dev",
    package_dir={'markitup_field': 'markitup_field'},
#    packages=['markitup_field', 'markitup_field.tests'],
    packages=['markitup_field'],
    py_modules=['markitup_field'],
#    data_files=[('static', static_files)],
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