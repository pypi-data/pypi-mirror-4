from setuptools import setup

setup(
    name='autoresponse',
    version='0.3',
    packages=['autoresponse'],
    license='Apache License 2.0',
    long_description=open('README').read(),
    install_requires=[
        'scrapy',
        ],
)

