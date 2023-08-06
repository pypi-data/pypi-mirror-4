from setuptools import setup, find_packages

setup(
    name='django-radius',
    version='0.1',
    description='A RADIUS authentication backend for Django',
    long_description=open('README.md').read(),
    author='Rob Golding',
    author_email='rob@robgolding.com',
    license='BSD',
    url='https://robgolding63.github.com/django-radius',
    download_url='https://github.com/robgolding63/django-radius/downloads',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyrad>=1.2,<2.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
