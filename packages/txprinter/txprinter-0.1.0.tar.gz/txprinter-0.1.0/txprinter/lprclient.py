from twisted.internet import defer, error
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from protocols.lpr import LPRClientProtocol

class QuickieClientFactory(ClientFactory):
    noisy = False
    def __init__(self, protocol):
        self.protocol = protocol
    def __repr__(self):
        return "Client Factory for %s" % (self.protocol,)

class LPRClient(object):
    def __init__(self, host='localhost', port=515):
        self.ep = clientFromString(reactor, "tcp:%s:%s" % (host, port))
        self.lprfactory = QuickieClientFactory(LPRClientProtocol)
        self.jobno = 1

    @defer.inlineCallbacks
    def printJob(self, queuename, jobdata, job_type='l', job_name=None):
        p = yield self.ep.connect(self.lprfactory)
        control = p._gencontrol(self.jobno, job_name, job_name)
        self.jobno += 1
        yield p.command_receive(queuename)
        yield p.subcommand_receive_controlfile(len(control))
        yield p.send_file(control)
        yield p.subcommand_receive_datafile(len(jobdata))
        yield p.send_file(jobdata)
        p.transport.loseConnection()
