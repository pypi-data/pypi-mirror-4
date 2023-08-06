# Copyright (c) 2012-2013 SwiftStack, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import math
import logging
import msgpack
import statlib.stats
from datetime import datetime
from mako.template import Template
from collections import OrderedDict

import eventlet
import eventlet.pools
from eventlet.green.httplib import CannotSendRequest

import ssbench
import ssbench.swift_client as client
from ssbench.run_state import RunState

from pprint import pprint, pformat


REPORT_TIME_FORMAT = '%F %T UTC'


def _container_creator(storage_url, token, container):
    http_conn = client.http_connection(storage_url)
    try:
        client.head_container(storage_url, token, container,
                              http_conn=http_conn)
    except client.ClientException:
        client.put_container(storage_url, token, container,
                             http_conn=http_conn)


def _gen_cleanup_job(object_info):
    return {
        'type': ssbench.DELETE_OBJECT,
        'container': object_info[0],
        'name': object_info[1],
    }


class Master:
    def __init__(self, queue, quiet=False):
        queue.watch(ssbench.STATS_TUBE)
        queue.ignore('default')
        self.queue = queue
        self.quiet = quiet

    def process_result_to(self, job, processor, label=''):
        job.delete()
        result = msgpack.loads(job.body)
        logging.debug('RESULT: %13s %s/%-17s %s/%s %s',
                      result['type'], result['container'], result['name'],
                      '%7.4f' % result.get('first_byte_latency')
                      if result.get('first_byte_latency', None) else ' (none)',
                      '%7.4f' % result.get('last_byte_latency')
                      if result.get('last_byte_latency', None) else '(none) ',
                      result.get('trans_id', ''))
        if label and not self.quiet:
            if 'first_byte_latency' in result:
                if result['first_byte_latency'] < 1:
                    sys.stderr.write('.')
                elif result['first_byte_latency'] < 3:
                    sys.stderr.write('o')
                elif result['first_byte_latency'] < 10:
                    sys.stderr.write('O')
                else:
                    sys.stderr.write('*')
            elif 'exception' in result:
                sys.stderr.write('X')
            else:
                sys.stderr.write('_')
            sys.stderr.flush()
        processor(result)

    def do_a_run(self, concurrency, job_generator, result_processor, priority,
                 storage_url, token, mapper_fn=None, label='', noop=False):
        if label and not self.quiet:
            print >>sys.stderr, label + """
  .  <  1s first-byte-latency
  o  <  3s first-byte-latency
  O  < 10s first-byte-latency
  * >= 10s first-byte-latency
  X    work job raised an exception
  _    no first-byte-latency available
            """.rstrip()
        active = 0
        for job in job_generator:
            if mapper_fn is not None:
                work_job = mapper_fn(job)
                if not work_job:
                    if noop:
                        job['container'] = 'who_cares'
                        job['name'] = 'who_cares'
                    else:
                        logging.warning('Unable to fill in job %r', job)
                        continue
                else:
                    job = work_job
            job['storage_url'] = storage_url
            job['token'] = token

            if active >= concurrency:
                result_job = self.queue.reserve()
                self.process_result_to(result_job, result_processor,
                                       label=label)
                active -= 1
            self.queue.put(msgpack.dumps(job), priority=priority)
            active += 1

        # Drain the results
        while active > 0:
            result_job = self.queue.reserve()
            self.process_result_to(result_job, result_processor, label=label)
            active -= 1
        if label and not self.quiet:
            sys.stderr.write('\n')
            sys.stderr.flush()

    def run_scenario(self, auth_url, user, key, storage_url, token, scenario,
                     noop=False, with_profiling=False):
        """
        Runs a CRUD scenario, given cluster parameters and a Scenario object.

        :auth_url: Authentication URL for the Swift cluster
        :user: Account/Username to use (format is <account>:<username>)
        :key: Password for the Account/Username
        :scenario: Scenario object describing the benchmark run
        :returns: Collected result records from workers
        """

        run_state = RunState()

        self.drain_stats_queue()
        if not storage_url or not token:
            logging.debug('Authenticating to %s with %s/%s', auth_url, user,
                          key)
            storage_url, token = client.get_auth(auth_url, user, key)
        else:
            logging.debug('Using token %s at %s', token, storage_url)

        logging.info(u'Starting scenario run for "%s"', scenario.name)

        # Ensure containers exist
        if not noop:
            logging.info('Ensuring %d containers (%s_*) exist; '
                         'concurrency=%d...',
                         len(scenario.containers), scenario.container_base,
                         scenario.container_concurrency)
            pool = eventlet.GreenPool(scenario.container_concurrency)
            for container in scenario.containers:
                pool.spawn_n(_container_creator, storage_url, token, container)
            pool.waitall()

        self.queue.use(ssbench.WORK_TUBE)

        # Enqueue initialization jobs
        if not noop:
            logging.info('Initializing cluster with stock data (up to %d '
                         'concurrent workers)', scenario.user_count)

            self.do_a_run(scenario.user_count, scenario.initial_jobs(),
                          run_state.handle_initialization_result,
                          ssbench.PRIORITY_SETUP, storage_url, token)

        logging.info('Starting benchmark run (up to %d concurrent '
                     'workers)', scenario.user_count)
        if noop:
            logging.info('  (not actually talking to Swift cluster!)')

        if with_profiling:
            import cProfile
            prof = cProfile.Profile()
            prof.enable()
        self.do_a_run(scenario.user_count, scenario.bench_jobs(),
                      run_state.handle_run_result,
                      ssbench.PRIORITY_WORK, storage_url, token,
                      mapper_fn=run_state.fill_in_job,
                      label='Benchmark Run:', noop=noop)
        if with_profiling:
            prof.disable()
            prof_output_path = '/tmp/do_a_run.%d.prof' % os.getpid()
            prof.dump_stats(prof_output_path)
            logging.info('PROFILED main do_a_run to %s', prof_output_path)

        if not noop:
            logging.info('Deleting population objects from cluster')
            self.do_a_run(scenario.user_count,
                          run_state.cleanup_object_infos(),
                          lambda *_: None,
                          ssbench.PRIORITY_CLEANUP, storage_url, token,
                          mapper_fn=_gen_cleanup_job)

        return run_state.run_results

    def drain_stats_queue(self):
        job = self.queue.reserve(timeout=0)
        while job:
            job.delete()
            job = self.queue.reserve(timeout=0)

    def write_rps_histogram(self, stats, csv_file):
        csv_file.write('"Seconds Since Start","Requests Completed"\n')
        for i, req_count in enumerate(stats['time_series']['data'], 1):
            csv_file.write('%d,%d\n' % (i, req_count))

    def scenario_template(self):
        return """
${scenario.name}
  C   R   U   D       Worker count: ${'%3d' % agg_stats['worker_count']}   Concurrency: ${'%3d' % scenario.user_count}
%% ${'%02.0f  %02.0f  %02.0f  %02.0f' % (crud_pcts[0], crud_pcts[1], crud_pcts[2], crud_pcts[3])}      Ran ${start_time} to ${stop_time} (${'%.0f' % round(duration)}s)

% for label, stats, sstats in stat_list:
% if stats['req_count']:
${label}
       Count: ${'%5d' % stats['req_count']}  Average requests per second: ${'%5.1f' % stats['avg_req_per_sec']}
                            min       max      avg      std_dev  ${'%02d' % nth_pctile}%-ile  ${'%15s' % ''}  Swift TX ID for worst latency
       First-byte latency: ${stats['first_byte_latency']['min']} - ${stats['first_byte_latency']['max']}  ${stats['first_byte_latency']['avg']}  (${stats['first_byte_latency']['std_dev']})  ${stats['first_byte_latency']['pctile']}  (all obj sizes)  ${stats['worst_first_byte_latency'][1] if 'worst_first_byte_latency' in stats else ''}
       Last-byte  latency: ${stats['last_byte_latency']['min']} - ${stats['last_byte_latency']['max']}  ${stats['last_byte_latency']['avg']}  (${stats['last_byte_latency']['std_dev']})  ${stats['last_byte_latency']['pctile']}  (all obj sizes)  ${stats['worst_last_byte_latency'][1] if 'worst_last_byte_latency' in stats else ''}
% for size_str, per_size_stats in sstats.iteritems():
% if per_size_stats:
       First-byte latency: ${per_size_stats['first_byte_latency']['min']} - ${per_size_stats['first_byte_latency']['max']}  ${per_size_stats['first_byte_latency']['avg']}  (${per_size_stats['first_byte_latency']['std_dev']})  ${per_size_stats['first_byte_latency']['pctile']}  ${'(%8s objs)' % size_str}  ${per_size_stats['worst_first_byte_latency'][1] if 'worst_first_byte_latency' in per_size_stats else ''}
       Last-byte  latency: ${per_size_stats['last_byte_latency']['min']} - ${per_size_stats['last_byte_latency']['max']}  ${per_size_stats['last_byte_latency']['avg']}  (${per_size_stats['last_byte_latency']['std_dev']})  ${per_size_stats['last_byte_latency']['pctile']}  ${'(%8s objs)' % size_str}  ${per_size_stats['worst_last_byte_latency'][1] if 'worst_last_byte_latency' in per_size_stats else ''}
% endif
% endfor

% endif
% endfor
"""

    def generate_scenario_report(self, scenario, stats):
        """Format a report based on calculated statistics for an executed
        scenario.

        :stats: A python data structure with calculated statistics
        :returns: A report (string) suitable for printing, emailing, etc.
        """

        template = Template(self.scenario_template())
        tmpl_vars = {
            'crud_pcts': scenario.crud_pcts,
            'stat_list': [
                ('TOTAL', stats['agg_stats'], stats['size_stats']),
                ('CREATE', stats['op_stats'][ssbench.CREATE_OBJECT],
                 stats['op_stats'][ssbench.CREATE_OBJECT]['size_stats']),
                ('READ', stats['op_stats'][ssbench.READ_OBJECT],
                 stats['op_stats'][ssbench.READ_OBJECT]['size_stats']),
                ('UPDATE', stats['op_stats'][ssbench.UPDATE_OBJECT],
                 stats['op_stats'][ssbench.UPDATE_OBJECT]['size_stats']),
                ('DELETE', stats['op_stats'][ssbench.DELETE_OBJECT],
                 stats['op_stats'][ssbench.DELETE_OBJECT]['size_stats']),
            ],
            'agg_stats': stats['agg_stats'],
            'nth_pctile': stats['nth_pctile'],
            'start_time': datetime.utcfromtimestamp(
                stats['time_series']['start_time']
            ).strftime(REPORT_TIME_FORMAT),
            'stop_time': datetime.utcfromtimestamp(
                stats['time_series']['stop']).strftime(REPORT_TIME_FORMAT),
            'duration': stats['time_series']['stop']
            - stats['time_series']['start_time'],
        }
        return template.render(scenario=scenario, stats=stats, **tmpl_vars)

    def calculate_scenario_stats(self, scenario, results, nth_pctile=95):
        """Given a list of worker job result dicts, compute various statistics.

        :results: A list of worker job result dicts
        :returns: A stats python dict which looks like:
            SERIES_STATS = {
                'min': 1.1,
                'max': 1.1,
                'avg': 1.1,
                'std_dev': 1.1,
                'median': 1.1,
            }
            {
                'agg_stats': {
                    'worker_count': 1,
                    'start': 1.1,
                    'stop': 1.1,
                    'req_count': 1,
                    'avg_req_per_sec': 1.1, # req_count / (stop - start)?
                    'first_byte_latency': SERIES_STATS,
                    'last_byte_latency': SERIES_STATS,
                },
                'worker_stats': {
                    1: {  # keys are worker_ids
                        'start': 1.1,
                        'stop': 1.1,
                        'req_count': 1,
                        'avg_req_per_sec': 1.1, # req_count / (stop - start)?
                        'first_byte_latency': SERIES_STATS,
                        'last_byte_latency': SERIES_STATS,
                    },
                    # ...
                },
                'op_stats': {
                    CREATE_OBJECT: { # keys are CRUD constants: CREATE_OBJECT, READ_OBJECT, etc.
                        'req_count': 1, # num requests of this CRUD type
                        'avg_req_per_sec': 1.1, # total_requests / sum(last_byte_latencies)
                        'first_byte_latency': SERIES_STATS,
                        'last_byte_latency': SERIES_STATS,
                        'size_stats': {
                            'small': { # keys are size_str values
                                'req_count': 1, # num requests of this type and size
                                'avg_req_per_sec': 1.1, # total_requests / sum(last_byte_latencies)
                                'first_byte_latency': SERIES_STATS,
                                'last_byte_latency': SERIES_STATS,
                            },
                            # ...
                        },
                    },
                    # ...
                },
                'size_stats': {
                    'small': { # keys are size_str values
                        'req_count': 1, # num requests of this size (for all CRUD types)
                        'avg_req_per_sec': 1.1, # total_requests / sum(last_byte_latencies)
                        'first_byte_latency': SERIES_STATS,
                        'last_byte_latency': SERIES_STATS,
                    },
                    # ...
                },
                'time_series': {
                    'start': 1, # epoch time of first data point
                    'data': [
                        1, # number of requests finishing during this second
                        # ...
                    ],
                },
            }
        """
        # Each result looks like:
        # {
        #   'worker_id': 1,
        #   'type': 'get_object',
        #   'size': 4900000,
        #   'first_byte_latency': 0.9137639999389648,
        #   'last_byte_latency': 0.913769006729126,
        #   'completed_at': 1324372892.360802,
        #}
        # OR
        # {
        #   'worker_id': 1,
        #   'type': 'get_object',
        #   'completed_at': 1324372892.360802,
        #   'exception': '...',
        # }
        logging.info('Calculating statistics for %d result items...',
                     len(results))
        agg_stats = dict(start=2 ** 32, stop=0, req_count=0)
        op_stats = {}
        for crud_type in [ssbench.CREATE_OBJECT, ssbench.READ_OBJECT,
                          ssbench.UPDATE_OBJECT, ssbench.DELETE_OBJECT]:
            op_stats[crud_type] = dict(
                req_count=0, avg_req_per_sec=0,
                size_stats=OrderedDict.fromkeys(scenario.sizes_by_name.keys()))

        req_completion_seconds = {}
        start_time = 0
        completion_time_max = 0
        completion_time_min = 2 ** 32
        stats = dict(
            nth_pctile=nth_pctile,
            agg_stats=agg_stats,
            worker_stats={},
            op_stats=op_stats,
            size_stats=OrderedDict.fromkeys(scenario.sizes_by_name.keys()))
        for result in results:
            if 'exception' in result:
                # skip but log exceptions
                logging.warn('calculate_scenario_stats: exception from '
                             'worker %d: %s',
                             result['worker_id'], result['exception'])
                continue
            completion_time = int(result['completed_at'])
            if completion_time < completion_time_min:
                completion_time_min = completion_time
                start_time = completion_time - result['last_byte_latency']
            if completion_time > completion_time_max:
                completion_time_max = completion_time
            req_completion_seconds[completion_time] = \
                1 + req_completion_seconds.get(completion_time, 0)
            result['start'] = (
                result['completed_at'] - result['last_byte_latency'])

            # Stats per-worker
            if result['worker_id'] not in stats['worker_stats']:
                stats['worker_stats'][result['worker_id']] = {}
            self._add_result_to(stats['worker_stats'][result['worker_id']],
                                result)

            # Stats per-file-size
            if not stats['size_stats'][result['size_str']]:
                stats['size_stats'][result['size_str']] = {}
            self._add_result_to(stats['size_stats'][result['size_str']],
                                result)

            self._add_result_to(agg_stats, result)
            self._add_result_to(op_stats[result['type']], result)

            # Stats per-operation-per-file-size
            if not op_stats[result['type']]['size_stats'][result['size_str']]:
                op_stats[result['type']]['size_stats'][result['size_str']] = {}
            self._add_result_to(
                op_stats[result['type']]['size_stats'][result['size_str']],
                result)
        agg_stats['worker_count'] = len(stats['worker_stats'].keys())
        self._compute_req_per_sec(agg_stats)
        self._compute_latency_stats(agg_stats, nth_pctile)
        for worker_stats in stats['worker_stats'].values():
            self._compute_req_per_sec(worker_stats)
            self._compute_latency_stats(worker_stats, nth_pctile)
        for op_stat, op_stats_dict in op_stats.iteritems():
            if op_stats_dict['req_count']:
                self._compute_req_per_sec(op_stats_dict)
                self._compute_latency_stats(op_stats_dict, nth_pctile)
                for size_str, size_stats in \
                        op_stats_dict['size_stats'].iteritems():
                    if size_stats:
                        self._compute_req_per_sec(size_stats)
                        self._compute_latency_stats(size_stats, nth_pctile)
                    else:
                        op_stats_dict['size_stats'].pop(size_str)
        for size_str, size_stats in stats['size_stats'].iteritems():
            if size_stats:
                self._compute_req_per_sec(size_stats)
                self._compute_latency_stats(size_stats, nth_pctile)
            else:
                stats['size_stats'].pop(size_str)
        time_series_data = [req_completion_seconds.get(t, 0)
                            for t in range(completion_time_min,
                                           completion_time_max + 1)]
        stats['time_series'] = dict(start=completion_time_min,
                                    start_time=start_time,
                                    stop=completion_time_max,
                                    data=time_series_data)

        return stats

    def _compute_latency_stats(self, stat_dict, nth_pctile):
        try:
            for latency_type in ('first_byte_latency', 'last_byte_latency'):
                stat_dict[latency_type] = self._series_stats(
                    stat_dict[latency_type], nth_pctile)
        except KeyError:
            logging.exception('stat_dict: %r', stat_dict)
            raise

    def _compute_req_per_sec(self, stat_dict):
        stat_dict['avg_req_per_sec'] = round(stat_dict['req_count'] /
                                             (stat_dict['stop'] -
                                              stat_dict['start']), 6)

    def _add_result_to(self, stat_dict, result):
        if 'start' not in stat_dict or result['start'] < stat_dict['start']:
            stat_dict['start'] = result['start']
        if 'stop' not in stat_dict or \
                result['completed_at'] > stat_dict['stop']:
            stat_dict['stop'] = result['completed_at']
        if 'req_count' not in stat_dict:
            stat_dict['req_count'] = 1
        else:
            stat_dict['req_count'] += 1
        self._rec_latency(stat_dict, result)

    def _series_stats(self, sequence, nth_pctile):
        pre_filter_count = len(sequence)
        sequence = filter(None, sequence)
        logging.debug('_series_stats pre/post seq len: %d/%d',
                      pre_filter_count, len(sequence))
        if not sequence:
            # No data available
            return dict(min=' N/A  ', max='  N/A  ', avg='  N/A  ',
                        pctile='  N/A  ', std_dev='  N/A  ', median='  N/A  ')
        sequence.sort()
        try:
            n, (minval, maxval), mean, std_dev, skew, kurtosis = \
                statlib.stats.ldescribe(sequence)
        except ZeroDivisionError:
            # Handle the case of a single-element sequence (population standard
            # deviation divides by N-1)
            minval = sequence[0]
            maxval = sequence[0]
            mean = sequence[0]
            std_dev = 0
        return dict(
            min='%6.3f' % minval,
            max='%7.3f' % maxval,
            avg='%7.3f' % mean,
            pctile='%7.3f' % self.pctile(sequence, nth_pctile),
            std_dev='%7.3f' % statlib.stats.lsamplestdev(sequence),
            median='%7.3f' % statlib.stats.lmedianscore(sequence))

    def pctile(self, sequence, nth_pctile):
        seq_len = len(sequence)
        rank = seq_len * nth_pctile / 100.0
        if float(int(rank)) == rank:
            # integer rank means we interpolate between two values
            rank = int(rank)
            return (sequence[rank - 1] + sequence[rank]) / 2.0
        else:
            return sequence[int(math.ceil(rank)) - 1]

    def _rec_latency(self, stats_dict, result):
        for latency_type in ('first_byte_latency', 'last_byte_latency'):
            if latency_type in stats_dict:
                stats_dict[latency_type].append(result[latency_type])
            else:
                stats_dict[latency_type] = [result[latency_type]]
            if result[latency_type] is not None:
                worst_key = 'worst_%s' % latency_type
                if worst_key not in stats_dict \
                        or result[latency_type] > stats_dict[worst_key][0]:
                    stats_dict[worst_key] = (round(result[latency_type], 6),
                                             result['trans_id'])
