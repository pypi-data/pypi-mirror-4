#!/usr/bin/env python
#-*- coding:utf-8 -*-
import argparse
import datetime
import json
import logging
import os
import random
import shlex
import socket
import subprocess
import sys
import time

from haigha.connection import Connection as haigha_Connection
from haigha.connections import RabbitConnection
from haigha.message import Message

from queue_connection import connect


logger = logging.getLogger('cronq')

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger.addHandler(NullHandler())

def get_args_from_cli():
    parser = argparse.ArgumentParser(description='Start CronQ Runner')

    args = parser.parse_args()
    return args

def channel_closed_cb(ch):
    print "AMQP channel closed; close-info: %s" % (
      ch.close_info,)
    ch = None
    return

def create_connection_closed_cb(connection):
    def connection_closed_cb():
        print "AMQP broker connection closed; close-info: %s" % (
          connection.close_info,)
        connection = None
    return connection_closed_cb




def setup():
    args = get_args_from_cli()

    conn = connect()
    if conn is None:
        return
    conn._close_cb = create_connection_closed_cb(conn)

    # Create message channel
    channel = conn.channel()

    channel.basic.qos(prefetch_count=1)
    runner = create_runner(channel)

    channel.basic.consume(
        queue='cronq_jobs',
        consumer=runner,
        no_ack=False,
    )

    while True:
        conn.read_frames()


def create_runner(channel):

    def run_something(msg):
        tag = msg.delivery_info['delivery_tag']
        def ack():
            channel.basic.ack(tag)

        def reject(requeue=True):
            channel.basic.reject(tag, requeue=requeue)

        def publish_result(body):
            msg = Message(json.dumps(body), {})
            channel.basic.publish(msg, 'cronq', 'cronq_results')

        data = json.loads(str(msg.body))
        cmd = data.get('cmd')
        args = shlex.split(str(cmd))
        print 'starting'
        publish_result({
            'job_id': data.get('job_id'),
            'run_id': data.get('run_id'),
            'start_time': str(datetime.datetime.utcnow()),
            'type': 'starting',
        })
        print args
        start = time.time()
        try:
            proc = subprocess.Popen(args)
        except OSError as exc:
            print 'Failed', exc
            end = time.time()
            publish_result({
                'job_id': data.get('job_id'),
                'run_id': data.get('run_id'),
                'run_time': end - start,
                'type': 'failed',
            })
            return reject(requeue=False)
        print 'waiting'

        proc.wait()
        end = time.time()
        publish_result({
            'job_id': data.get('job_id'),
            'run_id': data.get('run_id'),
            'return_code': proc.returncode,
            'run_time': end - start,
            'type': 'finished',
        })
        print 'done', proc.returncode, data.get('run_id')

        ack()

    return run_something


def load_module(module_name):
    return importlib.import_module(module_name)

def load_consumer(consumer_str):
    logger.debug('Loading consumer {0}'.format(consumer_str))
    return load_module_object(consumer_str)

def load_module_object(module_object_str):
    module_name, obj_name = module_object_str.split(':')
    module = load_module(module_name)
    return getattr(module, obj_name)


class ConsumerPool(object):
    def __init__(self, channel, klass, greenlet_maker, size=1):
        self._channel = channel
        self._pool = gevent.queue.Queue()
        self._klass = klass
        self._gm = greenlet_maker
        for i in range(size):
            self._create()

    def _create(self):
        logger.debug('Creating consumer instance: {0}'.format(self._klass.__name__))
        self._pool.put(self._klass())

    def handle(self, msg):
        def func():
            consumer = self._pool.get()
            amqp_proxy = AMQPProxy(self._channel, msg)

            def put_back(successful_greenlet):
                logger.debug('Successful run, putting consumer back')
                self._pool.put(consumer)

            def recreate(failed_greenlet):
                logger.info('Consume failed, shutting down consumer')
                if not amqp_proxy.has_responded_to_message:
                    amqp_proxy.reject(requeue=True)
                shutdown_greenlet = gevent.Greenlet(
                    consumer.shutdown,
                    failed_greenlet.exception
                )
                def create_wrapper(*args):
                    self._create()
                shutdown_greenlet.link(create_wrapper)
                shutdown_greenlet.start()

            greenlet = self._gm(consumer.consume, amqp_proxy, msg)
            greenlet.link_value(put_back)
            greenlet.link_exception(recreate)
            greenlet.start()
        self._gm(func).start()

class AMQPProxy(object):

    def __init__(self, channel, msg):
        self._channel = channel
        self._msg = msg
        self._terminal_state = False

    @property
    def tag(self):
        return self._msg.delivery_info['delivery_tag']

    @property
    def has_responded_to_message(self):
        return self._terminal_state

    def ack(self):
        self._error_if_already_terminated()
        self._channel.basic.ack(self.tag)

    def nack(self):
        self._error_if_already_terminated()
        self._channel.basic.nack(self.tag)

    def reject(self, requeue=True):
        self._error_if_already_terminated()
        self._channel.basic.reject(self.tag, requeue=requeue)

    def publish(self, exchange, routing_key, headers, body):
        msg = Message(body, headers)
        self._channel.basic.publish(msg, exchange, routing_key)

    def _error_if_already_terminated(self):
        if self._terminal_state == True:
            raise Exception('Already responded to message!')
        else:
            self._terminal_state = True


def message_pump_greenthread(connection):
    logging.debug('Starting message pump')
    exit_code = 0
    try:
        while connection is not None:
            # Pump
            connection.read_frames()

            # Yield to other greenlets so they don't starve
            gevent.sleep()
    except Exception as exc:
        logger.exception(exc)
        exit_code = 1
    finally:
        logging.debug('Leaving message pump')
    return exit_code

def main():
    greenlet = setup()
    if greenlet is not None:
        greenlet.start()
        greenlet.join()
        sys.exit(greenlet.get())


if __name__ == '__main__':
    main()
