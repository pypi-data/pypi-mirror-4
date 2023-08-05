import os.path
from setuptools import setup, find_packages


install_requires = ["Flask", "PyYAML", "Markdown"]

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="stanley",
    version="1.3.4",
    description="Flat file blog tool bult on Jinja2 templates",
    long_description="",
    url="https://github.com/glenswinfield/stanley",
    author="Glen Swinfield",
    author_email="glen.swinfield@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    test_suite="tests.get_tests",
)
