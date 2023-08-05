from setuptools import setup, find_packages

setup(
    name='django-fakeimg',
    version="0.1.2",
    license="BSD",

    install_requires = [
        "Pillow",
    ],

    description='A django port of fakeimg.pl',

    author='Shu Cao',
    author_email='shucao@gmail.com',

    url='http://github.com/scao/django-fakeimg',

    include_package_data=True,

    packages=['fakeimg'],

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
    )
