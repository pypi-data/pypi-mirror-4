from setuptools import setup, find_packages


setup(name = 'solr_recipe',
    description = 'Buildout recipe that installs and configures Apache Solr. The default setup works with haystack 1.2.3.',
    license='Apache',
    version = '1.0',
    url = 'http://github.com/espenak/solr_recipe',
    author = 'Espen Angell Kristiansen',
    author_email = 'post@espenak.net',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['ez_setup', 'fabfile']),
    install_requires = ['distribute', 'Django', 'Jinja2'],
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'zc.buildout': [
            'default = solr_recipe.install:InstallSolr'
            ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Framework :: Buildout',
        'Programming Language :: Python'
    ]
)
