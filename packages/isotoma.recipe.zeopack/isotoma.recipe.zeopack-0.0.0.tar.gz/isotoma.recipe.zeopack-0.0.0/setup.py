from setuptools import setup, find_packages

version = '0.0.0'

setup(
    name = 'isotoma.recipe.zeopack',
    version = version,
    description = "Buildout recipes for zeopack.",
    url = "http://pypi.python.org/pypi/isotoma.recipe.zeopack",
    long_description = open("README.rst").read() + "\n" + \
                       open("CHANGES.txt").read(),
    classifiers = [
        "Framework :: Buildout",
        "Framework :: Buildout :: Recipe",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords = "buildout zeopack",
    author = "John Carr",
    author_email = "john.carr@isotoma.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    package_data = {
    },
    namespace_packages = ['isotoma', 'isotoma.recipe'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'zc.buildout',
    ],
    entry_points = {
        "zc.buildout": [
            "default = isotoma.recipe.zeopack.recipe:Recipe",
        ],
    }
)
