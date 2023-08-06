# Copyright (c) 2013 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from __future__ import absolute_import

import sys
import os
import os.path
import warnings
from functools import wraps
from contextlib import contextmanager
from socket import getfqdn

from config import Config, ConfigError, ConfigInputStream
import slimta.system

from .validation import ConfigValidation
from .celery import get_app as get_celery_app


class SlimtaState(object):

    _global_config_files = [os.path.expanduser('~/.slimta.conf'),
                            '/etc/slimta.conf']

    def __init__(self, program, attached=True):
        self.config_file = os.getenv('SLIMTA_CONFIG', None)
        self.program = program
        self.attached = attached
        self.ap = None
        self.cfg = None
        self.edges = {}
        self.queues = {}
        self.relays = {}
        self._celery = None

    @contextmanager
    def _with_chdir(self, new_dir):
        old_dir = os.getcwd()
        os.chdir(new_dir)
        yield old_dir
        os.chdir(old_dir)

    def _try_configs(self, files):
        for config_file in files:
            config_file = os.path.expanduser(config_file)
            config_dir = os.path.abspath(os.path.dirname(config_file))
            config_base = os.path.basename(config_file)
            with self._with_chdir(config_dir):
                if os.path.exists(config_base):
                    return Config(config_base)
        return None

    def load_config(self, config_file):
        if self.cfg:
            return True

        files = self._global_config_files
        if config_file:
            files = [config_file]

        self.cfg = self._try_configs(files)
        if self.cfg:
            ConfigValidation.check(self.cfg)
            return True
        else:
            return False

    def drop_privileges(self):
        process_options = self.cfg.process.get(self.program)
        user = process_options.get('user')
        group = process_options.get('group')
        if user or group:
            if os.getuid() == 0:
                slimta.system.drop_privileges(user, group)
            else:
                warnings.warn('Only superuser can drop privileges.')

    def redirect_streams(self):
        process_options = self.cfg.process.get(self.program)
        flag = process_options.get('daemon', False)
        if flag and not self.attached:
            so = process_options.get('stdout')
            se = process_options.get('stderr')
            si = process_options.get('stdin')
            slimta.system.redirect_stdio(so, se, si)

    def daemonize(self):
        flag = self.cfg.process.get(self.program).get('daemon', False)
        if flag and not self.attached:
            slimta.system.daemonize()

    def _start_relay(self, name, options=None):
        if name in self.relays:
            return self.relays[name]
        if not options:
            options = getattr(self.cfg.relay, name)
        new_relay = None
        if options.type == 'mx':
            from slimta.relay.smtp.mx import MxSmtpRelay
            ehlo_as = options.get('ehlo_as')
            new_relay = MxSmtpRelay(ehlo_as=ehlo_as)
        elif options.type == 'static':
            from slimta.relay.smtp.static import StaticSmtpRelay
            host = options.host
            port = options.get('port', 25)
            ehlo_as = options.get('ehlo_as')
            new_relay = StaticSmtpRelay(host, port, ehlo_as=ehlo_as)
        elif options.type == 'maildrop':
            from slimta.maildroprelay import MaildropRelay
            executable = options.get('executable')
            new_relay = MaildropRelay(executable=executable)
        else:
            raise ConfigError('relay type does not exist: '+options.type)
        self.relays[name] = new_relay
        return new_relay

    def _start_queue(self, name, options=None):
        if name in self.queues:
            return self.queues[name]
        if not options:
            options = getattr(self.cfg.queue, name)
        from .helpers import add_queue_policies
        new_queue = None
        if options.type == 'memory':
            from slimta.queue import Queue
            from slimta.queue.dict import DictStorage
            relay_name = options.get('relay')
            if not relay_name:
                raise ConfigError('queue sections must be given a relay name')
            relay = self._start_relay(relay_name)
            store = DictStorage()
            new_queue = Queue(store, relay)
        elif options.type == 'disk':
            from slimta.queue import Queue
            from slimta.diskstorage import DiskStorage
            relay_name = options.get('relay')
            if not relay_name:
                raise ConfigError('queue sections must be given a relay name')
            relay = self._start_relay(relay_name)
            env_dir = options.envelope_dir
            meta_dir = options.meta_dir
            tmp_dir = options.get('tmp_dir')
            store = DiskStorage(env_dir, meta_dir, tmp_dir)
            new_queue = Queue(store, relay)
        elif options.type == 'proxy':
            from slimta.queue.proxy import ProxyQueue
            relay_name = options.get('relay')
            if not relay_name:
                raise ConfigError('queue sections must be given a relay name')
            relay = self._start_relay(relay_name)
            new_queue = ProxyQueue(relay)
        elif options.type == 'celery':
            from slimta.celeryqueue import CeleryQueue
            relay_name = options.get('relay')
            if not relay_name:
                raise ConfigError('queue sections must be given a relay name')
            relay = self._start_relay(relay_name)
            new_queue = CeleryQueue(self.celery, relay, name)
        else:
            raise ConfigError('queue type does not exist: '+options.type)
        add_queue_policies(new_queue, options.get('policies', []))
        self.queues[name] = new_queue
        return new_queue

    @property
    def celery(self):
        if not self._celery:
            self._celery = get_celery_app(self.cfg)
        return self._celery

    def start_celery_queues(self):
        for name, options in dict(self.cfg.queue).items():
            if options.type == 'celery':
                self._start_queue(name, options)

    def _start_edge(self, name, options=None):
        if name in self.edges:
            return self.edges[name]
        if not options:
            options = getattr(self.cfg.edge, name)
        new_edge = None
        if options.type == 'smtp':
            from slimta.edge.smtp import SmtpEdge
            from .helpers import build_smtpedge_validators, build_smtpedge_auth
            ip = options.listener.get('interface', '127.0.0.1')
            port = int(options.listener.get('port', 25))
            queue_name = options.queue
            queue = self._start_queue(queue_name)
            kwargs = {}
            if options.get('tls'):
                kwargs['tls'] = dict(options.tls)
            kwargs['tls_immediately'] = options.get('tls_immediately', False)
            kwargs['validator_class'] = build_smtpedge_validators(options)
            kwargs['auth_class'] = build_smtpedge_auth(options)
            kwargs['command_timeout'] = 20.0
            kwargs['data_timeout'] = 30.0
            kwargs['max_size'] = 10485760
            kwargs['hostname'] = options.get('hostname')
            new_edge = SmtpEdge((ip, port), queue, **kwargs)
            new_edge.start()
        else:
            raise ConfigError('edge type does not exist: '+options.type)
        self.edges[name] = new_edge
        return new_edge

    def start_edges(self):
        for name, options in dict(self.cfg.edge).items():
            self._start_edge(name, options)

    def worker_loop(self):
        try:
            self.celery.Worker().run()
        except (KeyboardInterrupt, SystemExit):
            print

    def loop(self):
        from gevent.event import Event
        try:
            Event().wait()
        except (KeyboardInterrupt, SystemExit):
            print


# vim:et:fdm=marker:sts=4:sw=4:ts=4
