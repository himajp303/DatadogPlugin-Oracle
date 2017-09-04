# (C) Datadog, Inc. 2010-2016
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

# stdlib

# 3rd party

import cx_Oracle

# project
from checks import AgentCheck

EVENT_TYPE = SOURCE_TYPE_NAME = 'oracle'


class OracleCheck(AgentCheck):

    SERVICE_CHECK_NAME = 'oracle.can_connect'
    SYS_METRICS = {
        'Buffer Cache Hit Ratio':           'oracle.buffer_cachehit_ratio',
        'Cursor Cache Hit Ratio':           'oracle.cursor_cachehit_ratio',
        'Library Cache Hit Ratio':          'oracle.library_cachehit_ratio',
        'Shared Pool Free %':               'oracle.shared_pool_free',
        'Physical Reads Per Sec':           'oracle.physical_reads',
        'Physical Writes Per Sec':          'oracle.physical_writes',
        'Enqueue Timeouts Per Sec':         'oracle.enqueue_timeouts',
        'GC CR Block Received Per Second':  'oracle.gc_cr_receive_time',
        'Global Cache Blocks Corrupted':    'oracle.cache_blocks_corrupt',
        'Global Cache Blocks Lost':         'oracle.cache_blocks_lost',
        'Logons Per Sec':                   'oracle.logons',
        'Average Active Sessions':          'oracle.active_sessions',
        'Long Table Scans Per Sec':         'oracle.long_table_scans',
        'SQL Service Response Time':        'oracle.service_response_time',
        'User Rollbacks Per Sec':           'oracle.user_rollbacks',
        'Total Sorts Per User Call':        'oracle.sorts_per_user_call',
        'Rows Per Sort':                    'oracle.rows_per_sort',
        'Disk Sort Per Sec':                'oracle.disk_sorts',
        'Memory Sorts Ratio':               'oracle.memroy_sorts_ratio',
        'Database Wait Time Ratio':         'oracle.database_wait_time_ratio',
        'Enqueue Timeouts Per Sec':         'oracle.enqueue_timeouts',
        'Session Limit %':                  'oracle.session_limit_usage',
        'Session Count':                    'oracle.session_count',
        'Temp Space Used':                  'oracle.temp_space_used',
    }

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    def check(self, instance):
        self.log.debug('Running cx_Oracle version {0}'.format(cx_Oracle.version))
        server, user, password, tags, port, sid = self._get_config(instance)

        if not server or not user:
            raise Exception("Oracle host and user are needed")

        con = self._get_connection(server, user, password, port, sid)

        self._get_sys_metrics(con, tags)

        self._get_tablespace_metrics(con)

    def _get_config(self, instance):
        self.server = instance.get('server', None)
        user = instance.get('user', None)
        password = instance.get('password', None)
        tags = instance.get('tags', None)
        port = instance.get('port', None)
        sid = instance.get('sid', None)
        return (self.server, user, password, tags, port, sid)

    def _get_connection(self, server, user, password, port, sid):
        self.service_check_tags = [
            'server:%s' % server
        ]
        dsn = cx_Oracle.makedsn(server, port, sid)
        connect_string = '{0}/{1}@{2}'.format(user, password, dsn)
        try:
            con = cx_Oracle.connect(connect_string)
            self.log.debug("Connected to Oracle DB")
            self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.OK,
                               tags=self.service_check_tags)
        except Exception, e:
            self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.CRITICAL,
                               tags=self.service_check_tags)
            self.log.error(e)
            raise
        return con

    def _get_sys_metrics(self, con, tags):
        query = "SELECT METRIC_NAME, VALUE, BEGIN_TIME FROM GV$SYSMETRIC " \
            "ORDER BY BEGIN_TIME"
        cur = con.cursor()
        cur.execute(query)
        for row in cur:
            metric_name = row[0]
            metric_value = row[1]
            if metric_name in self.SYS_METRICS:
                self.gauge(self.SYS_METRICS[metric_name], metric_value, tags=tags)

    def _get_tablespace_metrics(self, con):
        query = "SELECT TABLESPACE_NAME, BYTES, MAXBYTES FROM sys.dba_data_files"
        cur = con.cursor()
        cur.execute(query)
        for row in cur:
            tablespace_tag = 'tablespace:%s' % row[0]
            used = row[1]
            size = row[2]
            in_use = used / size * 100
            self.gauge('oracle.tablespace.used', used, tags=[tablespace_tag])
            self.gauge('oracle.tablespace.size', size, tags=[tablespace_tag])
            self.gauge('oracle.tablespace.in_use', in_use, tags=[tablespace_tag])
