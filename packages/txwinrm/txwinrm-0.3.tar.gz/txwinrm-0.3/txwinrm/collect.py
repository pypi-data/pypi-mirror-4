##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from pprint import pformat
from twisted.internet import defer
from .client import WinrmClientFactory


class Result(object):

    def __repr__(self):
        return '\n' + pformat(vars(self), indent=4)


class ResultsAccumulator(object):

    def __init__(self):
        self.results = []

    def new_instance(self):
        self.results.append(Result())

    def add_property(self, name, value):
        setattr(self.results[-1], name, value)


class WinrmCollectClient(object):

    def __init__(self):
        self._client_factory = WinrmClientFactory()

    @defer.inlineCallbacks
    def do_collect(self, hostname, username, password, wqls):
        client = self._client_factory.create_winrm_client()
        results = {}
        for wql in wqls:
            accumulator = ResultsAccumulator()
            yield client.enumerate(hostname, username, password, wql,
                                   accumulator)
            results[wql] = accumulator.results
        defer.returnValue(results)


# ----- An example of useage...

if __name__ == '__main__':
    from pprint import pprint
    import logging
    from twisted.internet import reactor
    logging.basicConfig()
    winrm = WinrmCollectClient()

    @defer.inlineCallbacks
    def do_example_collect():
        results = yield winrm.do_collect(
            "gilroy", "Administrator", "Z3n0ss",
            ['Select Caption, DeviceID, Name From Win32_Processor',
             'select Name, Label, Capacity from Win32_Volume'])
        pprint(results)
        reactor.stop()

    reactor.callWhenRunning(do_example_collect)
    reactor.run()
