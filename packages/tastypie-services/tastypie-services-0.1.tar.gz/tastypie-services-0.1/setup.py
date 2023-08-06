from setuptools import setup


setup(
    name='tastypie-services',
    version='0.1',
    description='Service URLs for tastypie',
    long_description=open('README.rst').read(),
    author='Andy McKay',
    author_email='andym@mozilla.com',
    license='BSD',
    install_requires=['django-tastypie'],
    packages=['services'],
    url='https://github.com/andymckay/tastypie-services',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Django'
    ]
)
