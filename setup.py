"""
Setup script for PyPi
"""

from distutils.core import setup
setup(
    name='scrapy-twitter',
    version='0.1.9',
    description='Twitter API wrapper for scrapy',
    url='http://github.com/watsy0007/scrapy-twitter',
    author='watsy0007',
    author_email='watsy0007@gmail.com',
    license='MIT',
    py_modules=['scrapy_twitter'],
    install_requires=[
        'python-twitter'
    ],
    zip_safe=False)
