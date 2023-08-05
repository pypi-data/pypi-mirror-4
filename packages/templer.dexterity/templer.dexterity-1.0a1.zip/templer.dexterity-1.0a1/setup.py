from setuptools import setup, find_packages
import os

version = '1.0a1'

tests_require = [
    'Cheetah',
    'PasteScript',
    'templer.core',
    'templer.buildout',
    'templer.zope',
]

setup(name='templer.dexterity',
    version=version,
    description="templer templates for dexterity",
    long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords='plone dexterity paster templates zopeskel',
    author=' ZopeSkel/Templer Development Team',
    author_email='zopeskel@lists.plone.org',
    url='http://github.com/collective/templer.dexterity',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['templer'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'templer.plone',
        'templer.localcommands',
    ],
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
    entry_points="""
    # -*- Entry points: -*-
    [paste.paster_create_template]
    dexterity = templer.dexterity:Dexterity
    [templer.templer_sub_template]
    content_type = templer.dexterity.localcommands.dexterity:DexterityContent
    behavior = templer.dexterity.localcommands.dexterity:DexterityBehavior
    """,
    )
