from distutils.core import setup

setup(
    name='django-heap',
    description='Simple Heap analytics integration',
    long_description=open('README.rst').read(),
    version='0.0.1',
    packages=['heap'],
    package_data={
        'heap': [
            'templates/heap/*.html',
        ],
    },
    include_package_data=True,
    author='Monwara LLC',
    author_email='branko@monwara.com',
    url='https://bitbucket.org/monwara/django-heap',
    download_url='https://bitbucket.org/monwara/django-heap/downloads',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
)


