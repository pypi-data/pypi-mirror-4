# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq
import logging

from collections import defaultdict

from elevator.utils.snippets import sec_to_ms

from elevator.backend.worker import Worker
from elevator.backend.protocol import ServiceMessage
from elevator.backend.protocol import WORKER_HALT, WORKER_STATUS,\
                                      WORKER_LAST_ACTION


activity_logger = logging.getLogger("activity_logger")
errors_logger = logging.getLogger("errors_logger")


class Supervisor(object):
    """A remote control to lead them all

    Exposes an internal api to talk to database workers and
    give them orders.
    """
    def __init__(self, zmq_context, databases_store, timeout=3):
        self.databases_store = databases_store
        self.workers = defaultdict(dict)
        self.timeout = sec_to_ms(timeout)

        self.zmq_context = zmq_context
        self.socket = zmq_context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.bind('inproc://supervisor')

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def command(self, instruction,
                workers_ids=None, max_retries=3,
                timeout=None):
        """Command an action to workers.

        An optional list of workers ids can be provided
        as an argument, in order to restrain the command
        to specific workers.
        """
        workers_ids = workers_ids or self.workers.iterkeys()
        timeout = timeout or self.timeout
        responses = []

        for worker_id in workers_ids:
            if worker_id in self.workers:
                worker_socket = self.workers[worker_id]['socket']
                request = ServiceMessage.dumps(instruction)
                self.socket.send_multipart([worker_socket, request], flags=zmq.NOBLOCK)

                retried = 0
                while retried <= max_retries:
                    sockets = dict(self.poller.poll(self.timeout))

                    if sockets and sockets.get(self.socket) == zmq.POLLIN:
                        serialized_response = self.socket.recv_multipart(flags=zmq.NOBLOCK)[1]
                        responses.append(ServiceMessage.loads(serialized_response))
                        break
                    else:
                        retried += 1

                if retried == max_retries:
                    err_msg = "Instruction %s sent to %s failed. Retried %d times"
                    errors_logger.error(err_msg % (instruction, worker_id, retried))

        return responses

    def status(self, worker_id):
        """Fetches a worker status"""
        return self.command(WORKER_STATUS, [worker_id])

    def statuses(self):
        """Fetch workers statuses"""
        return self.command(WORKER_STATUS)

    def stop(self, worker_id):
        """Stop a specific worker"""
        self.command(WORKER_HALT, [worker_id])
        self.workers[worker_id]['thread'].join()
        self.workers.pop(worker_id)

    def stop_all(self):
        """Stop every supervised workers"""
        self.command(WORKER_HALT)

        for worker in self.workers.itervalues():
            worker['thread'].join()

        for _id in self.workers.keys():
            self.workers.pop(_id)

    def last_activity(self, worker_id):
        """Asks a specific worker information about it's
        last activity

        Returns a tuple containing it's latest activity timestamp
        first, and the database affected by it in second
        """
        return self.command(WORKER_LAST_ACTION, [worker_id])

    def last_activity_all(self):
        """Asks every supervised workers informations about it's
        last activity

        Returns a list of tuples containing it's latest activity timestamp
        first, and the database affected by it in second
        """
        return self.command(WORKER_LAST_ACTION)

    def init_workers(self, count):
        """Starts `count` workers.

        Awaits for their id to be received (blocking), and
        registers their socket id and thread reference
        """
        pos = 0

        while pos < count:
            # Start a worker
            worker = Worker(self.zmq_context, self.databases_store)
            worker.start()

            socket_id, response = self.socket.recv_multipart()
            worker_id = ServiceMessage.loads(response)[0]

            self.workers[worker_id]['socket'] = socket_id
            self.workers[worker_id]['thread'] = worker
            pos += 1
