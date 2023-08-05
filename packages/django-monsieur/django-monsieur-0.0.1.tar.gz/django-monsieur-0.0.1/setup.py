from setuptools import setup, find_packages

setup(
    name='django-monsieur',
    version='0.0.1',
    description='.',
    long_description=open('README.rst').read(),
    author='Matt Forbes',
    author_email='matt.r.forbes@gmail.com',
    url='https://github.com/emef/django-monsieur',
    license='BSD',
    packages=find_packages(exclude=('tests', 'example',)),
    tests_require=[
        'django>=1.3,<1.5',
    ],
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
