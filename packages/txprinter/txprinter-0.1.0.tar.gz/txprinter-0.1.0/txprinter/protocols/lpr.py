import getpass
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred

class LPRClientProtocol(Protocol):
    def dataReceived(self, data):
        for c in data:
            if (self._lastdef is not None):
                ld, self._lastdef = self._lastdef, None
                if c == '\000':
                    ld.callback(True)
                else:
                    ld.errback(c)

    def command_receive(self, queue):
        self._lastdef = Deferred()
        payload = '\002{0}\012'.format(queue)
        self.transport.write(payload)
        return self._lastdef

    def _gencontrol(self, jobno, filename, job_name=None):
        if (job_name is None):
            job_name = filename
        self.jobno = jobno
        self.dfname = "dfA%03i.%s" % (jobno, self.transport.getHost().host)
        control = 'H{0}\012N{1}\012J{2}\012P{3}\012l{4}\012U{4}\012'.format(self.transport.getHost().host,
                                                                            filename,
                                                                            job_name,
                                                                            getpass.getuser(),
                                                                            self.dfname)
        return control


    def subcommand_receive_controlfile(self, length):
        payload = '\002{0} cfA{2}{1}\012'.format(length, self.transport.getHost().host, "%03i" % self.jobno)
        self._lastdef = Deferred()
        self.transport.write(payload)
        return self._lastdef

    def send_file(self, data):
        self._lastdef = Deferred()
        self.transport.write(data)
        self.transport.write('\000')
        return self._lastdef

    def subcommand_receive_datafile(self, length):
        payload = '\003{0} {1}\012'.format(length, self.dfname)
        self._lastdef = Deferred()
        self.transport.write(payload)
        return self._lastdef
