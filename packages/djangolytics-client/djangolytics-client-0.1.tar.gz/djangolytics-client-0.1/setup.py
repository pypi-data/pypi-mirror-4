import djangolytics

from setuptools import setup, find_packages


setup(
    name='djangolytics-client',
    version=djangolytics.__version__,
    description="ALPHA - don't use!",
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=['django',],
    author='Daniel Greenfeld',
    author_email='pydanny@gmail.com',
    url='http://pydanny.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
