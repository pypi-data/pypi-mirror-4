from setuptools import setup

setup(
    name="django-multiform",
    version="0.1",
    description="Wrap several django forms into one form-like object",
    keywords="django, forms, multiform",
    author="Baptiste Mispelon <bmispelon@gmail.com>",
    url="https://github.com/bmispelon/django-multiform/",
    license="BSD",
    packages=["multiform"],
    zip_safe=False,
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3"
    ],
)
