from setuptools import setup, find_packages


setup(
    name='python-ipagare',
    version='0.0.5',
    description='python api to ipagare webservices',
    long_description=open("README.md").read(),
    author=u'Marcel Nicolay',
    author_email='marcelnicolay@gmail.com',
    url='http://github.com/quatix/python-ipagare',
    install_requires=open("requirements.txt").read().split("\n"),
    packages=find_packages(),
    package_dir={"ipagare": "ipagare"},
)
