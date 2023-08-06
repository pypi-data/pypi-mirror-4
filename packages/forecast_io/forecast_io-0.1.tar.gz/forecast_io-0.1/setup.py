from setuptools import setup

setup(
    name='forecast_io',
    version='0.1',
    description="forecast.io API wrapper in Python.",
    long_description="",
    keywords='forecast.io, api, wrapper',
    author='Bohdan Kanskyi',
    author_email='kanskib@gmail.com',
    url='https://github.com/kanski/forecast_io',
    license='BSD',
    packages=['forecast_io'],
    zip_safe=False,
    install_requires=['requests>=1.2.0'],
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
