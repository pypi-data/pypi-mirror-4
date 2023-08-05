from twisted.internet import defer
from carnifex.ssh.session import SSHSession
from twisted.internet.protocol import ProcessProtocol
from zope.interface.declarations import implements
from twisted.internet.interfaces import IProcessTransport

def connectShell(connection, processProtocol, commandLine='', env={},
                 usePTY=None, childFDs=None, *args, **kwargs):
    """Opens a SSHSession channel and connects a ProcessProtocol to it

    @param connection: the SSH Connection to open the session channel on
    @param processProtocol: the ProcessProtocol instance to connect to the process
    @param commandLine: the command line to execute the process
    @param env: optional environment variables to set for the process
    @param usePTY: if set, request a PTY for the process
    @param childFDs: custom child file descriptors for the process
    """
    processOpenDeferred = defer.Deferred()
    process = SSHShellTransport(processProtocol, commandLine, env, usePTY, childFDs,
                         *args, **kwargs)
    process.processOpen = processOpenDeferred.callback
    process.openFailed = processOpenDeferred.errback

    connection.openChannel(process)
    return processOpenDeferred


class SSHShellProcess(SSHProcess):
    def sessionOpen(self, specificData):
        """Callback triggered when the session channel has opened
        """
        # Make sure the protocol use the session channel as transport
        self.processProtocol.makeConnection(self)
        # Request shell
        shell_d = self.requestShell()
        shell_d.addCallbacks(self.processOpen, self.openFailed)


class ShellProcessInductorProtocol(ProcessProtocol, ProcessInductor):
    """A ProcessProtocol that acts like a ProcessInductor.
    
    This can be used for shell like processes
    """

    currentProcess = None

    def __init__(self, prompt):
        self.prompt = prompt

    def execute(self, processProtocol, command, env={}, 
        path=None, uid=None, gid=None, usePTY=0, childFDs=None):
        assert not self.currentProcess, "Can not run concurrent processes"
        self.currentProcess = processProtocol
        process = ShellProcess(self)
        self.transport.write(command + '\n')
        return process

    def childDataReceived(self, childFD, data):
        if self.currentProcess:
            output, sep, extra = data.partition(self.prompt)
            # Relay data to child process
            self.currentProcess.childDataReceived(self, childFD, output)
            if True:
                # Include extra output (DebugSh prints prompt first)
                self.childDataReceived(self, childFD, extra)
            if sep:
                # We got the prompt, so the process has ended
                reason = failure.Failure(ProcessDone(status=self.status))
                self.currentProcess.processEnded(reason)
                self.currentProcess = None


class ShellProcess(object):
    """Represent a sub-process started within a shell-like prompt
    """

    implements(IProcessTransport)

    def __init__(self, transport):
        self.transport = transport

    def closeStdin(self):
        self.closeChildFD(0)

    def closeStdout(self):
        self.closeChildFD(1)

    def closeStderr(self):
        self.closeChildFD(2)

    def closeChildFD(self, descriptor):
        if descriptor == 0:
            #TODO: ?
            pass

    def writeToChild(self, childFD, data):
        if childFD == 0:
            self.transport.write(data)

    def loseConnection(self):
        self.closeStdin()
        self.closeStderr()
        self.closeStdout()
        self.transport.loseConnection()

    def signalProcess(self, signal):
        """"No way to signal a shell process
        """

    def write(self, data):
        self.transport.write(data)

    def writeSequence(self, data):
        self.write(''.join(data))
