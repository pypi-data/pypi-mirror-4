from setuptools import setup, find_packages

setup(
    name="isotoma.recipe.ploneprefetch",
    version='0.0.2',
    maintainer = "John Carr",
    maintainer_email = "john.carr@isotoma.com",
    description="ZC Buildout recipe for installing Plone quickly",
    long_description = open("README.rst").read(),
    license="ZPL 2.1",
    keywords="zope2 buildout",
    url = 'http://github.com/isotoma/isotoma.recipe.ploneprefetch',
    classifiers = [
        "Framework :: Buildout",
        "Framework :: Buildout :: Recipe",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
    packages=find_packages(),
    include_package_data=True,
    namespace_packages=['isotoma', 'isotoma.recipe'],
    install_requires=['zc.buildout', 'setuptools'],
    zip_safe=False,
    entry_points={'zc.buildout': ['default = isotoma.recipe.ploneprefetch:Recipe']},
    )
