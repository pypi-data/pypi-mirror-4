from setuptools import setup, find_packages

setup(
    name="brodul.recipe.template",
    version="1.2.1",
    author="Andraz Brodnik",
    author_email="brodul@brodul.org",
    url="http://github.com/brodul/amplecode.recipe.template",
    description="Buildout recipe for making files out of Jinja2 templates",
    long_description=open("README.rst").read(),
    classifiers=(
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Pre-processors",
    ),
    keywords="zc.buildout recipe template Jinja2",
    license="BSD",
    packages=find_packages(),
    namespace_packages=("brodul", "brodul.recipe"),
    install_requires=("setuptools", "zc.recipe.egg", "Jinja2", "zope.dottedname"),
    zip_safe=True,
    entry_points="""
        [zc.buildout]
        default = brodul.recipe.template:Recipe
    """,
)
