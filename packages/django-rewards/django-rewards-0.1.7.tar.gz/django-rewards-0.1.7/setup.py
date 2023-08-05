from setuptools import setup, find_packages

import rewards


setup(
    name='django-rewards',
    packages=find_packages(),
    include_package_data=True,
    version=rewards.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=rewards.__author__,
    author_email='admin@incuna.com',
    url='http://github.com/incuna/django-rewards/',
    install_requires=[
        'django-crispy-forms>=1.1.4',
        'django-extensible-profiles>=1.2'
    ],
    zip_safe=False,
)
