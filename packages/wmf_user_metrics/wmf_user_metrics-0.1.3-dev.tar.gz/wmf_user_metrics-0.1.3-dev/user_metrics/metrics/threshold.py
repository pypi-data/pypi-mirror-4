
__author__ = "Ryan Faulkner"
__date__ = "December 6th, 2012"
__license__ = "GPL (version 2 or later)"

from user_metrics.config import logging

from datetime import timedelta
import collections
import os
import user_metrics.utils.multiprocessing_wrapper as mpw
import user_metric as um
from user_metrics.etl.aggregator import decorator_builder, boolean_rate
from user_metrics.metrics import query_mod
from user_metrics.utils import format_mediawiki_timestamp
from dateutil.parser import parse as date_parse


class Threshold(um.UserMetric):
    """
        Boolean measure: Did an editor reach some threshold of activity (e.g.
        n edits, words added, pages created, etc.) within t time.

            `https://meta.wikimedia.org/wiki/Research:Metrics/threshold(t,n)`

        As a UserMetric type this class utilizes the process() function
        attribute to produce an internal list of metrics by user handle
        (typically ID but user names may also be specified). The execution
        of process() produces a nested list that stores in each element:

            * User ID
            * boolean flag to indicate whether edit threshold was reached
                in time given

        usage e.g.: ::

            >>> import user_metrics.etl.threshold as t
            >>> for r in t.Threshold().process([13234584]).__iter__(): print r
            (13234584L, 1)
    """

    # Structure that defines parameters for Threshold class
    _param_types = {
        'init': {
            't': [int, 'The time in minutes until the threshold.', 24],
            'n': [int, 'Revision threshold that is '
                       'to be exceeded in time `t`.', 1],
        },
        'process': {
            'survival_': [bool, 'Indicates whether this is '
                                'to be processed as the survival metric.',
                         False],
        }
    }

    # Define the metrics data model meta
    _data_model_meta = {
        'id_fields': [0],
        'date_fields': [],
        'float_fields': [],
        'integer_fields': [],
        'boolean_fields': [1],
    }

    _agg_indices = {
        'list_sum_indices': _data_model_meta['boolean_fields'],
    }

    @um.pre_metrics_init
    def __init__(self, **kwargs):
        super(Threshold, self).__init__(**kwargs)

    @staticmethod
    def header():
        return ['user_id', 'has_reached_threshold']

    @um.UserMetric.pre_process_metric_call
    def process(self, users, **kwargs):
        """
            This function gathers threahold (survival) metric data by: ::

                1. selecting all new user registrations within the timeframe
                    and in the user list (empty means select all withing the
                    timeframe.)
                2. For each user id find the number of revisions before (after)
                    the threshold (survival) cut-off time t

            - Parameters:
                - **user_handle** - String or Integer (optionally lists).
                    Value or list of values representing user handle(s).

            **NOTA BENE** - kwarg "survival" is used to execute has this
                determine survival rather than a threshold metric
        """

        # Get registration dates for users
        users = query_mod.user_registration_date(users,
                                                 self.project, None)
        # Process results
        args = [self.project, self.namespace, self.n,
                self.t, self.log_, self.survival_]
        self._results = mpw.build_thread_pool(users, _process_help,
                                              self.k_, args)
        return self


def _process_help(args):
    """ Used by Threshold::process() for forking.
        Should not be called externally. """

    ThresholdArgsClass = collections.namedtuple('ThresholdArgs',
                                                'project namespace n t '
                                                'log_progress survival ')
    user_data = args[0]
    state = args[1]
    thread_args = ThresholdArgsClass(state[0], state[1], state[2], state[3],
                                     state[4], state[5])

    if thread_args.log_progress:
        logging.info(__name__ + ' :: Processing revision data ' +
                                '(%s users) by user... (PID = %s)' % (
                                    len(user_data), os.getpid()))
        logging.info(__name__ + ' :: ' + str(thread_args))

    # only proceed if there is user data
    if not len(user_data):
        return []

    results = list()
    dropped_users = 0
    for r in user_data:
        try:
            threshold_ts = format_mediawiki_timestamp(date_parse(r[1]) +
                                                      timedelta(hours=
                                                      int(thread_args.t)))
            uid = long(r[0])
            count = query_mod.rev_count_query(uid,
                                              thread_args.survival,
                                              thread_args.namespace,
                                              thread_args.project,
                                              threshold_ts)
        except query_mod.UMQueryCallError:
            dropped_users += 1
            continue

        if count < thread_args.n:
            results.append((r[0], 0))
        else:
            results.append((r[0], 1))

    if thread_args.log_progress:
        logging.info(__name__ + '::Processed PID = %s.  '
                                'Dropped users = %s.' % (
                                    os.getpid(), str(dropped_users)))

    return results


# ==========================
# DEFINE METRIC AGGREGATORS
# ==========================

# Build "rate" decorator
threshold_editors_agg = boolean_rate
threshold_editors_agg = decorator_builder(Threshold.header())(
    threshold_editors_agg)

setattr(threshold_editors_agg, um.METRIC_AGG_METHOD_FLAG, True)
setattr(threshold_editors_agg, um.METRIC_AGG_METHOD_NAME,
        'threshold_editors_agg')
setattr(threshold_editors_agg, um.METRIC_AGG_METHOD_HEAD, ['total_users',
                                                           'threshold_reached',
                                                           'rate'])
setattr(threshold_editors_agg, um.METRIC_AGG_METHOD_KWARGS, {'val_idx': 1})

# testing
if __name__ == "__main__":
    for r in Threshold(namespace=[0, 4]).process([13234584, 156171],
                                                 num_threads=0,
                                                 log_progress=True).__iter__():
        print r
