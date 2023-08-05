from setuptools import setup, find_packages
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.4.2'

setup(name='Pyll',
    version=version,
    description="An MVC architecture web framework.",
    long_description="""An over-simplified web framework that utilizes the best-of-breed database and rendering engines. Suitable for any web application. Currently used in production in many web applications worldwide.""",
    classifiers=['Environment :: Web Environment'],
    keywords='web framework sqlalchemy',
    author='Noel Morgan',
    author_email='noel@pyll.org',
    url='http://www.pyll.org',
    license='MPL 2.0',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Paste>=1.7.5.1",
        "PasteScript>=1.7.5",
        "Beaker>=1.6.4",
        "FormEncode>=1.2.4",
        "Jinja2>=2.6",
        "Genshi>=0.6",
        "WebError>=0.10.3",
        "WebHelpers>=1.3",
        "psycopg2>=2.4",
        "transaction>=1.3",
        "zope.sqlalchemy>=0.7.1",
        "Pygments>=1.5",
        "MarkupSafe>=0.15",
        "decorator>=3.4.0",
        "SQLAlchemy>=0.7.9",
        "WebOb>=0.5.1",
        "PyDNS>=2.3.6",
        "Cheetah>=2.4.4"
    ],
    setup_requires=["PasteScript>=1.7.5"],
    entry_points="""
    [paste.paster_create_template]
    Pyll = pyll.tmplt:PyllTemplate
    """,)
