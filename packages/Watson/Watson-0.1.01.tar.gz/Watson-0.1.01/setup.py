from setuptools import setup, find_packages
import os

readme = os.path.join(os.path.dirname(__file__),'README.md')

setup(
    name='Watson',
    version='0.1.01',
    packages = find_packages(),
    include_package_data = True,
    author = "Babbaco",
    license='LICENSE.txt',
    long_description=open(readme).read(),
    description="The Chatbot that won America's hearts in the 80's is back! And this time, he means business!",
    url="https://github.com/Babbaco/Watson",
    install_requires=[
        "Twisted >= 12.2.0",
        "pinder==1.0.1",
        "wokkel == 0.7.0",
    ],
)