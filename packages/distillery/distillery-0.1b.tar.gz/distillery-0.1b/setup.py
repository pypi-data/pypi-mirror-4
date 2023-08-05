# -*- coding: utf-8 -*-
from distutils.core import setup


setup(
    name='distillery',
    version='0.1b',
    author=u'jean-philippe serafin',
    author_email='serafinjp@gmail.com',
    py_modules=('distillery',),
    url='https://github.com/Birdback/distillery',
    license='MIT licence',
    description='fixture utils for python ORMs',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)
