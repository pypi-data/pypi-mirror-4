=========================
solr_recipe
=========================

Buildout recipe that installs and configures Apache Solr. The recipe was made to
make it easy to setup Solr for Haystack. It has only been tested with
Haystack 1.2.3 and Solr 3.6.2.


Requirements
############

- Java 1.5 or greater from Oracle, OpenJDK or IMB. Gnu GCJ does not work. Run
  ``java -version`` to see what version you have installed if any.


Usage
#####

1. Add something like this to your ``buildout.cfg``::

    [buildout]
    ...
    parts = 
        ...
        solr
    ...

    [solr]
    recipe = solr_recipe
    solr_version = 3.6.2
    loglevel = INFO

2. The configuration above will work with Haystack. It installs a ``run_solr.sh``
   script in ``bin/``, and stores data in ``var/solr/data/``.
3. Run ``bin/buildout``.
4. Add ``schema.xml`` to ``var/solr/home/``. See ``solr_classpath`` for
   information about how this works.
5. Run ``bin/run_solr.sh``


Haystack?
=========
If you use Haystack, you should use::
    
        $ python manage.py build_solr_schema -f var/solr/home/conf/schema.xml

in step 3. See the ``run_solr_extra_startup_commands`` option below for how
to automate this.



Options
#############

``solr_version`` (**required**)
    The solr version to download from the ``mirror``.
``mirror``
    The Apache mirror to download from. Defaults to
    http://archive.apache.org/dist/lucene/solr/.
``java_executable``
    The Java executable to use in ``run_solr.sh``. Defaults to ``java``.
``solr_logconfig_tplfile``
    A Jinja2 template used to generate the solr ``logging.properties`` file.
    It gets all options added to the section as template variables, so
    ``loglevel`` and any other options you add will be available in the
    template. If no template file is specified, we use this template::

        .level = {{ loglevel }}

        # Write to the console:
        handlers = java.util.logging.ConsoleHandler

``loglevel``
    Specifies the loglevel for the ``solr_logconfig_tplfile``.
    Defaults to ``INFO``.
``solr_datadir``
    The directory where solr should store data. This is forwarded to
    solr via ``-Dsolr.data.dir`` in ``run_solr.sh``. Defaults to
    ``var/<sectionname>/data/``, where ``<sectionname>`` is the name
    of the buildout config section (``solr`` in the example above).
    The directory is created (recursively) if it does not exist.
``solr_home``
    Instead of using our example config-directory, you can configure your own
    using this option. Defaults to ``var/<sectionname>/home/``, which is copied
    from the `solr_recipe/files/example-solr3.6-config/`_-directory in the
    python package if it does not exists (links to the latest version - select
    the tag matching your version to view the actual files). The default
    directory does not include a ``schema.xml``.
``solr_classpath``
    Add extra directories to the Java classpath. Added to ``run_solr.sh`` with
    the ``-classpath`` option. Refer to ``java -help`` for more info about the
    format. You can use this to provide a directory where you override any
    config files in ``solr_home``. Defaults to
    ``var/<sectionname>/config_overrides``.
``run_solr_extra_startup_commands``
    Extra shell commands to run before starting solr in ``run_solr.sh``.
    Typically used to generate the Haystack schema automatically before
    starting solr. Example::

        [solr]
        recipe = solr_recipe
        ...
        run_solr_extra_startup_commands =
            echo "Starting Apache Solr"
            python ${buildout:directory}/manage.py build_solr_schema -f ${buildout:directory}/var/solr/home/conf/schema.xml

``run_solr_extra_shutdown_commands``
    Just like ``run_solr_extra_startup_commands``, but these are added to
    ``run_solr.sh`` after the command to start/run Solr. Example::

        [solr]
        recipe = solr_recipe
        ...
        run_solr_extra_shutdown_commands =
            echo "Solr was stopped. Exited with exit code $?"


.. note::
    We create ``var/<sectionname>/config_overrides`` even when it is not on the
    ``solr_classpath``. This is simply because it does not hurt, and detecting if
    it is on the classpath is just unneeded complexity.


.. _`solr_recipe/files/example-solr3.6-config/`: https://github.com/espenak/solr_recipe/tree/master/solr_recipe/files/example-solr3.6-config
