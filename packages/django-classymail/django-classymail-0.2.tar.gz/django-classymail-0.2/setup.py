from setuptools import setup


setup(
    name="django-classymail",
    version="0.2",
    description='E-mails in Django. Classy.',
    author='Rafal Stozek',
    license='BSD',

    packages=['classymail', 'classymail.templatetags'],

    install_requires=[
        'premailer',
        'cssselect',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
