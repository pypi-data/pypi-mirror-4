from setuptools import setup

setup(
    name = "elephunk",
    version = '0.0.1',
    description = "PostgreSQL Investigation Console",
    long_description = "PostgreSQL Investigation Console",
    url = "https://github.com/pitluga/elephunk",
    author = "Tony Pitluga",
    author_email = "tony.pitluga@gmail.com",
    license = "MIT",

    packages = ["elephunk"],
    scripts = ["bin/elephunk"],
    install_requires = [
        "Momoko==0.5.0",
        "psycopg2==2.4.5",
        "tornado==2.4",
        "wsgiref==0.1.2",
        "PyYAML==3.10"
    ]
)

