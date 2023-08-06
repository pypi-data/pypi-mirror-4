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

from os.path import realpath

# Project paths & parameters
# ==========================

__project_home__ = realpath('../..') + '/'
__web_home__ = ''.join([__project_home__, 'src/api/'])
__data_file_dir__ = ''.join([__project_home__, 'data/'])

__query_module__ = 'query_calls_sql'
__user_thread_max__ = 100
__rev_thread_max__ = 50


# MediaWiki Database connection settings
# ======================================

connections = {
    'slave': {
        'user': 'research',
        'host': '127.0.0.1',
        'db': 'prod',
        'passwd': '46c2f5d9481',
        'port': 3307},
    's1': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': 'prod',
        'passwd': '46c2f5d9481',
        'port': 3307},
    's5': {
        'user': 'research',
        'host': '127.0.0.1',
        # 'db': '',
        'passwd': '46c2f5d9481',
        'port': 3307},
}


PROJECT_DB_MAP = {
    'enwiki': 's1',
    'dewiki': 's5',
    'itwiki': 's2',
}

# SSH Tunnel Parameters
# =====================

TUNNEL_DATA = {
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
    }
}