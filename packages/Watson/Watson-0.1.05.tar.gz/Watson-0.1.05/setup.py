from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as README:
    DESCRIPTION = README.read()

setup(
    name='Watson',
    version='0.1.05',
    packages = find_packages(),
    include_package_data = True,
    author = "Babbaco",
    license='LICENSE.txt',
    long_description=DESCRIPTION,
    description="The Chatbot that won America's hearts in the 80's is back! And this time, he means business!",
    url="https://github.com/Babbaco/Watson",
    install_requires=[
        "Twisted >= 12.2.0",
        "pinder==1.0.1",
        "wokkel == 0.7.0",
    ],
)