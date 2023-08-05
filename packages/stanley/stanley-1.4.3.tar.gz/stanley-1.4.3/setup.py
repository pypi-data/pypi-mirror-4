import os.path
from setuptools import setup, find_packages


install_requires = ["Flask", "PyYAML", "Markdown", "Flask-Script"]

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="stanley",
    version="1.4.3",
    description="Flat file blog tool bult on Jinja2 templates",
    long_description="\n\n".join(open(os.path.join(base_dir, "README.rst"), "r").read()),
    url="https://github.com/glenswinfield/stanley",
    author="Glen Swinfield",
    author_email="glen.swinfield@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    test_suite="tests.get_tests",
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ]
)
