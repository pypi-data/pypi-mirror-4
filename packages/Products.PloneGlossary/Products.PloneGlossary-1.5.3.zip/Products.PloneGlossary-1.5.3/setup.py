from setuptools import setup, find_packages

version = '1.5.3'
long_description = open("README.txt").read() + "\n\n"
long_description += open("CHANGES.rst").read()
long_description = long_description.decode('utf8')

setup(
    name='Products.PloneGlossary',
    version=version,
    long_description=long_description,
    description="Highlight Plone content terms, mouseover shows the term definition as tooltip.",
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 3.2",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='plone glossary',
    author='Ingeniweb',
    author_email='support@ingeniweb.com',
    url='https://github.com/collective/Products.PloneGlossary',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'wicked',
        ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
