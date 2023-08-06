#!/usr/bin/env python
# -*- coding: utf-8 -*-

class RPCTransport(object):
    """Base class for all transports."""

class RPCRequestResponseClient(object):
    """A very simple client-server transport. Expects to deliver one message,
    fetching one reply afterwards."""

    def send(self, msg, timeout=None):
        raise RuntimeError('Not implemented')

    def receive(self, timeout=None):
        raise RuntimeError('Not implemented')

class RPCRequestResponseServer(object):
    """Server for RequestResponse transport."""

    def receive(self, timeout=None):
        """Receives a new message."""
        raise RuntimeError('Not implemented')

    def reply(self, timeout=None):
        """Replies with a message."""
        raise RuntimeError('Not implemented')
