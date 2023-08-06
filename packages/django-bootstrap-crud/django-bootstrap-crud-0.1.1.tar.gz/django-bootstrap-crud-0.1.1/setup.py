from setuptools import setup

setup(
    name='django-bootstrap-crud',
    version='0.1.1',
    url='https://github.com/garciaguimeras/django-bootstrap-crud',
    author='Noel Garcia Guimeras',
    author_email='garcia.guimeras@gmail.com',
    license='Apache License 2.0',
    packages=['bootstrap_crud', 'bootstrap_crud.templatetags', 'bootstrap_crud.celldesigner'],
    include_package_data=True,
    description='CRUD support for Django-Bootstrap projects',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
)
