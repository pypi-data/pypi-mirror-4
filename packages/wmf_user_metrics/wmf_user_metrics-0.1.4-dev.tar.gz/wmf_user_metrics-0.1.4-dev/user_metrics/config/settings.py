"""
    The configuration file for the user metrics project.  This module defines
    the project level variables used to tune the execution of user metric
    operations, set the path of resource dependencies, and define the database
    hosts for various projects.

    The init file for the config sub-package stores the details for the logger.


    Project Settings
    ~~~~~~~~~~~~~~~~

    - **__project_home__**      : Home directory for the project
    - **__web_home__**          : Home directory for Flask extension (api)
    - **__data_file_dir__**     : Home directory for any ancillary data files
    - **__query_module__**      : Defines the name of the module under
    src/metrics/query that is used to retrieve backend data.
    - **__user_thread_max__**   : Integer that tunes the maximum number of
    threads on which to partition user metric computations based on users.
    - **__rev_thread_max__**    : Integer that tunes the maximum number of
    threads on which to partition user metric computations based on revisions.


    MediaWiki DB Settings
    ~~~~~~~~~~~~~~~~~~~~~

    Two dictionaries, **connections** which defines connection credentials
    for data stores and **PROJECT_DB_MAP** which defines a mapping from
    project instance to data store.

"""

from pkg_resources import WorkingSet , DistributionNotFound, VersionConflict
from user_metrics.config import logging

# Get working set of Pyhon modules
working_set = WorkingSet()


# Project paths & parameters
# ==========================

__instance_host__ = '127.0.0.1'
__instance_port__ = 5000

__project_home__            = '/Users/rfaulkner/projects/E3_analysis/'
__web_home__                = ''.join([__project_home__, 'user_metrics/api/'])
__data_file_dir__           = ''.join([__project_home__, 'data/'])

__query_module__            = 'user_metrics.query.query_calls_sql'
__user_thread_max__         = 100
__rev_thread_max__          = 50
__time_series_thread_max__  = 6

__cohort_data_instance__    = 'cohorts'
__cohort_db__               = 'usertags'
__cohort_meta_db__          = 'usertags_meta'
__cohort_meta_instance__    = 'prod'

__secret_key__ = 'thesecretis...youmustunderstandtherollbeforeyoucanrock'

try:
    working_set.require('Flask-Login>=0.1.2')
    __flask_login_exists__ = True
    logging.debug(__name__ + ' :: Using module flask.ext.login...')
except (DistributionNotFound, VersionConflict):
    __flask_login_exists__ = False
    logging.debug(__name__ + ' :: Can\'t find module flask.ext.login...')


# MediaWiki Database connection settings
# ======================================

connections = {
    'slave': {
        'user': 'metrics',
        'host': '127.0.0.1',
        'db': 'prod',
        'passwd': 'Ad3unahpooPieh7e',
        'port': 4000},
    __cohort_data_instance__: {
        'user': 'research_prod',
        'host': '127.0.0.1',
        'db': 'prod',
        'passwd': 'Ph6BeeSh2rei',
        'port': 4000},
    's1': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': 'prod',
        'passwd': '46c2f5d9481',
        'port': 3307},
    's2': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': 'prod',
        'passwd': '46c2f5d9481',
        'port': 3308},
    's3': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': 'prod',
        'passwd': '46c2f5d9481',
        'port': 3309},
    's4': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': 'prod',
        'passwd': '46c2f5d9481',
        'port': 3310},
    's5': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': '',
        'passwd': '46c2f5d9481',
        'port': 3311},
}


PROJECT_DB_MAP = {
    'enwiki': 's1',
    'dewiki': 's5',
    'itwiki': 's2',
    'commonswiki': 's4',
}

# SSH Tunnel Parameters
# =====================

TUNNEL_DATA = {
    'db1047': {
        'cluster_host': 'stat1.wikimedia.org',
        'db_host': 'db1047.eqiad.wmnet',
        'user': 'rfaulk',
        'remote_port': 3306,
        'tunnel_port': 4000
    },
    's1': {
        'cluster_host': 'stat1.wikimedia.org',
        'db_host': 's1-analytics-slave.eqiad.wmnet',
        'user': 'rfaulk',
        'remote_port': 3306,
        'tunnel_port': 3307
    },
    's2': {
        'cluster_host': 'stat1.wikimedia.org',
        'db_host': 's2-analytics-slave.eqiad.wmnet',
        'user': 'rfaulk',
        'remote_port': 3306,
        'tunnel_port': 3308
    },
    's3': {
        'cluster_host': 'stat1.wikimedia.org',
        'db_host': 's3-analytics-slave.eqiad.wmnet',
        'user': 'rfaulk',
        'remote_port': 3306,
        'tunnel_port': 3309
    },
    's4': {
        'cluster_host': 'stat1.wikimedia.org',
        'db_host': 's4-analytics-slave.eqiad.wmnet',
        'user': 'rfaulk',
        'remote_port': 3306,
        'tunnel_port': 3310
    },
    's5': {
        'cluster_host': 'stat1.wikimedia.org',
        'db_host': 's5-analytics-slave.eqiad.wmnet',
        'user': 'rfaulk',
        'remote_port': 3306,
        'tunnel_port': 3311
    },
}
