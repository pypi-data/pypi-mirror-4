from setuptools import setup


setup(
    name="django-geetar",
    version=__import__('geetar').get_version().replace(' ', '-'),
    packages=[
        'geetar',
        'geetar.statusable',
        'geetar.templatetags',
        'geetar.tests'
    ],
    author="Instrument",
    author_email="chris.forrette@weareinstrument.com",
    description="A swiss army knife for your Django project, including a smattering of helpful code",
    keywords="django, helpers",
    url="https://github.com/Instrument/django-geetar",
    include_package_data=True,
    install_requires=[
        'django>=1.4'
    ],
    classifiers=[
        'Framework :: Django',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)

