from setuptools import setup, find_packages

setup(
    name = "sikahelloworld",
    version = "1.0.1",
    url = 'http://ondrejsika.com/libraries/python-viminput',
    author = 'Ondrej Sika',
    author_email = 'dev@ondrejsika.com',
    packages = find_packages(),
    requires = ["os", "tempfile"],
)
