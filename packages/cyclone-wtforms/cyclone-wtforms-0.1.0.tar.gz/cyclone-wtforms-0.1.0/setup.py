import sys

requires = ["twisted", "cyclone", "wtforms"]

# PyPy and setuptools don't get along too well, yet.
if sys.subversion[0].lower().startswith('pypy'):
    from distutils.core import setup
    extra = dict(requires=requires)
else:
    from setuptools import setup
    extra = dict(install_requires=requires)

setup(
    name="cyclone-wtforms",
    version="0.1.0",
    author="Alexandr Emelin",
    author_email="frvzmb@gmail.com",
    url="https://github.com/FZambia/cyclone-wtforms",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="WTForms for cyclone web server",
    keywords="twisted cyclone forms wtforms",
    packages=["cyclone_wtforms"],
    **extra
)

