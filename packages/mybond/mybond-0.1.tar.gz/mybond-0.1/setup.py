import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "mybond",
    version = "0.1",
    packages = find_packages(),
    author = "bond",
    author_email = "mhr.bond@gmail.com",
    description = "good job",
    url = "http://www.naver.com",
    include_package_data = True
)
