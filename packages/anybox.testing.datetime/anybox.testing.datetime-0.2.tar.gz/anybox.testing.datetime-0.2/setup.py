from setuptools import setup, find_packages

version = 0.2

setup(
    name = "anybox.testing.datetime",
    version = version,
    author="Georges Racinet",
    author_email="gracinet@anybox.fr",
    description="Various utilities related to date and time for testing purposes.",
    license="GPLv3+",
    long_description=open('README.txt').read() + open('CHANGES.txt').read(),
    url="https://bitbucket.org/anybox/anybox.testing.datetime",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['anybox', 'anybox.testing'],
    install_requires=['setuptools',],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Software Development :: Testing",
      ],
    entry_points = {},
    )


