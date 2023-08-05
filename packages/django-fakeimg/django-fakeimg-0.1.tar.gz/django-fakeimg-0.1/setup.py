import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-fakeimg",
    version = "0.1",
    packages = find_packages(),
    author = "Shu Cao",
    author_email = "shucao@gmail.com",
    description = "A django port of fakeimg.pl",
    url = "https://github.com/scao/django-fakeimg",
    include_package_data = True
)
