import logging
from os.path import join
from os.path import exists
import tarfile
from os import mkdir
from os import makedirs
from os import chmod
import posixpath
import urlparse
import urllib
from pkg_resources import resource_filename
from jinja2 import Template
import shutil


binscript_tpl = """#!/bin/sh

{% if run_solr_extra_startup_commands %}
{{ run_solr_extra_startup_commands }}
{% endif %}

cd {{ solrdir }}/example
{{ java_executable }} \\
    -Djava.util.logging.config.file={{ solr_logconfig_file }} \\
    -Dsolr.solr.home={{ solr_home }} \\
    -Dsolr.data.dir={{ solr_datadir }} \\
    -jar start.jar

{% if run_solr_extra_shutdown_commands %}
{{ run_solr_extra_shutdown_commands }}
{% endif %}
"""

logconfig_tpl = """
.level = {{ loglevel }}

# Write to the console:
handlers = java.util.logging.ConsoleHandler
"""



class InstallSolr(object):
    """
    """
    default_mirror = 'http://archive.apache.org/dist/lucene/solr/'

    def __init__(self, buildout, name, options):
        self.buildout, self.name, options = buildout, name, options
        self.log = logging.getLogger(self.name)

        partsdir = buildout['buildout']['parts-directory']
        self.installdir = join(partsdir, self.name)
        self.vardir = join(buildout['buildout']['directory'], 'var', self.name)

        defaults = {
            'mirror': self.default_mirror,
            'delete_downloaded_archive': False,
            'java_executable': 'java',
            'loglevel': 'INFO',
            'solr_logconfig_tplfile': None,
            'solr_datadir': join(self.vardir, 'data')
        }
        self.real_options = dict(defaults)
        self.real_options.update(options)

        solr_version = options['solr_version']
        archivedirname = 'apache-solr-{solr_version}'.format(solr_version=solr_version)
        self.archivename = '{0}.tgz'.format(archivedirname)
        self.download_url = urlparse.urljoin(self.real_options['mirror'],
            posixpath.join(solr_version, self.archivename))
        self.archivepath = join(partsdir, self.archivename)
        self.solrdir = join(self.installdir, archivedirname)
        self.default_solr_home = join(self.vardir, 'home')

    def _download(self):
        self.log.info('Downloading %s to %s', self.download_url, self.archivepath)
        urllib.urlretrieve(self.download_url, self.archivepath)

    def _extract(self):
        self.log.info('Extracting %s', self.archivename)
        tar = tarfile.open(self.archivepath)
        tar.extractall(self.installdir)
        tar.close()

    def _create_logging_config(self):
        solr_logconfig_tplfile = self.real_options['solr_logconfig_tplfile']
        if solr_logconfig_tplfile:
            tpl = open(solr_logconfig_tplfile, 'rb').read()
        else:
            tpl = logconfig_tpl
        logconfigfile = join(self.installdir, 'logging.properties')
        configdata = Template(tpl).render(**self.real_options)
        with open(logconfigfile, 'wb') as f:
            f.write(configdata)
        return logconfigfile

    def _create_solr_home(self):
        source = resource_filename(__name__, "files/example-solr3.6-config")
        dest = self.default_solr_home
        if not exists(dest):
            shutil.copytree(source, dest)
        return dest

    def _create_binscript(self):
        solr_logconfig_file = self._create_logging_config()
        if 'solr_home' in self.real_options:
            solr_home = self.real_options['solr_home']
        else:
            solr_home = self._create_solr_home()
        template = Template(binscript_tpl)
        run_solr_script_path = join(self.buildout['buildout']['bin-directory'], 'run_solr.sh')
        script = template.render(
            solrdir=self.solrdir,
            solr_logconfig_file=solr_logconfig_file,
            solr_home = solr_home,
            **self.real_options
        )
        with open(run_solr_script_path, 'wb') as f:
            f.write(script)
        chmod(run_solr_script_path, 0o755)

    def install(self):
        if not exists(self.installdir):
            mkdir(self.installdir)
        if not exists(self.vardir):
            makedirs(self.vardir)

        self.log.info('Installing Apache Solr from: %s', self.download_url)
        if not exists(self.archivepath):
            self._download()
            self._extract()
        elif not exists(self.solrdir):
            self._extract()
        if not exists(self.real_options['solr_datadir']):
            makedirs(self.real_options['solr_datadir'])
        self._create_binscript()
        managed_files = [self.installdir]
        if self.real_options['delete_downloaded_archive']:
            managed_files.append(self.archivepath)
        return managed_files

    def update(self):
        pass