import os.path
from setuptools import setup, find_packages


install_requires = ["flask", "Jinja2", "PyYAML", "Markdown"]

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="stanley",
    version="2.0.7",
    description="Flat file blog tool bult on markdown and Jinja2 templates",
    long_description="See https://github.com/glenswinfield/stanley for usage",
    url="https://github.com/glenswinfield/stanley",
    author="Glen Swinfield",
    author_email="glen.swinfield@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    test_suite="tests.get_tests",
    license='MIT',
    entry_points={
        'console_scripts': [
            'stanley = stanley.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
