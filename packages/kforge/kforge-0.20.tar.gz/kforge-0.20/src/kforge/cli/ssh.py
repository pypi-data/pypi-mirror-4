import os
import sys
import shlex
from subprocess import call
from subprocess import Popen, PIPE
import re
import kforge.regexps
from threading import Thread
from threading import Condition
import time
from kforge.dictionarywords import *
import traceback

# Todo: Test for cloning after adding changesets (Mercurial, Git, and Subversion).
# Todo: Test for pulling adding revisions from another clone (Mercurial, Git, and Subversion).

class SshCommandRunner(object):

    def __init__(self):

        try:
            lenArgv = len(sys.argv)
            assert lenArgv == 3, "SSH command needs 3 'argv' arguments (there are %s)." % lenArgv

            configPath = sys.argv[1]
            os.environ['KFORGE_SETTINGS'] = configPath
            try:
                from kforge.soleInstance import application
                import kforge.regexps
            except Exception, inst:
                raise Exception, "KForge error: Unable to import kforge"

            if not 'ssh' in application.registry.plugins:
                raise Exception, "KForge error: SSH functionality is not enabled"

            sshKeyId = sys.argv[2]
            try:
                assert sshKeyId
            except:
                msg = "SSH handler has bad configuration (key ID not given)."
                application.logger.error(msg)
                raise Exception, "Internal server error (1)"

            sshKeys = application.registry.sshKeys.findDomainObjects(id=sshKeyId)
            if not sshKeys:
                msg = "SSH handler has bad configuration (key ID '%s' not found in register)." % sshKeyId
                application.logger.error(msg)
                raise Exception, "Internal server error (2)"

            if len(sshKeys) > 1:
                msg = "SSH handler discovered model error (more than one ssh key for ID '%s')." % sshKeyId
                application.logger.error(msg)
                raise Exception, "Internal server error (3)"

            sshKey = sshKeys[0]

            try:
                if not sshKey.isConsummated:
                    sshKey.isConsummated = True
                    sshKey.save()
            except Exception, inst:
                msg = "SSH handler could not update 'isConsummated' attribute of ssh key '%s': %s" % (sshKeyId, inst)
                application.logger.error(msg)
                raise Exception, "Internal server error (4)"

            if not sshKey.person:
                msg = "SSH handler discovered model error (missing person for ssh key '%s')." % sshKeyId
                application.logger.error(msg)
                raise Exception, "Internal server error (5)"

            if not sshKey.person.name:
                msg = "SSH handler discovered model error (missing person name for person ID '%s')." % sshKey.person.id
                application.logger.error(msg)
                raise Exception, "Internal server error (6)"

            person = sshKey.person
            personName = person.name

            sshRequest = os.environ['SSH_ORIGINAL_COMMAND']

            if not sshRequest:
                msg = "SSH command not found in request from person '%s'." % personName
                application.logger.error(msg)
                raise Exception, "Bad request"
                
            application.logger.info("SSH request from person '%s' (key '%s'): %s" % (personName, sshKeyId, sshRequest))

            try:
                if sshRequest.startswith('git'):
                    commandClass = GitCommand
                elif sshRequest.startswith('hg'):
                    commandClass = MercurialCommand
                elif sshRequest.startswith('svn'):
                    commandClass = SubversionCommand
                else:
                    raise Exception, "SSH command is not supported: %s" % sshRequest

                command = commandClass(
                    sshRequest=sshRequest,
                    person=person,
                    application=application,
                )
                command.run()

            except ServiceNotFound, inst:
                msg = "Repository not found for SSH request from '%s': %s: %s." % (personName, sshRequest, inst)
                application.logger.warning(msg)
                raise Exception, "kforge: Service not found for requested path: %s" % command.urlPath
            except AccessDenied, inst:
                application.logger.info("Access denied for SSH request from '%s': %s: %s." % (personName, sshRequest, inst))
                raise Exception, "kforge: Access denied"
            except Exception, inst:
                trace = traceback.format_exc()
                application.logger.error("Error processing SSH request from '%s': %s: %s: %s" % (personName, sshRequest, inst, trace))
                raise Exception, "kforge: Internal server error (7)"

        except Exception, inst:
            print >>sys.stderr, inst
            sys.exit(-1)


class AccessDenied(Exception): pass


class BaseCommand(object):

    def __init__(self, sshRequest, application=None, person=None):
        self.sshRequest = sshRequest
        self.application = application
        self.logger = self.application.logger
        self.person = person
        self.isDebug = 'DEBUG' in self.application.dictionary[LOG_LEVEL]

    def run(self):
        self.splitSshRequest()
        self.validateRequest()
        self.initActionName()
        self.initUrlPath()
        self.initService()
        self.assertAccessAuthorized()
        self.rewriteRequestArgs()
        self.initShellCmd()
        self.call()

    def splitSshRequest(self):
        sshRequestParts = shlex.split(str(self.sshRequest))
        self.sshRequestCmd = sshRequestParts[0]
        self.sshRequestArgs = sshRequestParts[1:]

    def validateRequest(self):
        raise Exception, "Method not implemented."

    def initActionName(self):
        raise Exception, "Method not implemented."

    def initUrlPath(self):
        raise Exception, "Method not implemented."

    def initService(self):
        urlPathParts = self.urlPath.strip("'").strip('/').split('/')
        try:
            assert len(urlPathParts) == 2, "Service path needs two parts: %s" % self.urlPath

            projectName = urlPathParts[0]
            pattern = re.compile('^%s$' % kforge.regexps.projectName)
            assert pattern.match(projectName), "Project name '%s' is not valid" % projectName

            serviceName = urlPathParts[1]
            pattern = re.compile('^%s$' % kforge.regexps.serviceName)
            assert pattern.match(serviceName), "Service name '%s' is not valid" % serviceName

            project = self.application.registry.projects[projectName]
            service = project.services[serviceName]
        except Exception, inst:
            raise ServiceNotFound, inst
        self.service = service
        self.log("SSH request for access to service: %s" % self.service)
        self.servicePath = self.application.fileSystem.getServicePath(self.service)

    def rewriteRequestArgs(self):
        raise Exception, "Method not implemented."

    def assertAccessAuthorized(self):
        isAuthorised = self.isAccessAuthorised(
            actionName=self.actionName,
        )
        if not isAuthorised:
            raise AccessDenied, "SSH command is not authorised"

    def isAccessAuthorised(self, actionName):
        return self.application.accessController.isAccessAuthorised(
            person=self.person,
            protectedObject=self.service.plugin,
            actionName=actionName,
            project=self.service.project,
        )

    def initShellCmd(self):
        self.shellCmd = self.sshRequestCmd + " " + " ".join(self.sshRequestArgs)

    def call(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def log(self, line, isDebug=False, isError=False):
        if isDebug:
            self.logger.debug(line)
        elif isError:
            self.logger.error(line)
        else:
            self.logger.info(line)


class GitCommand(BaseCommand):

    def validateRequest(self):
        if self.sshRequestCmd == 'git':
            if len(self.sshRequestArgs) != 2:
                msg = "Git command '%s' needs two arguments: %s" % (
                    self.sshRequestCmd, self.sshRequestArgs)
                raise Exception, msg
            if self.sshRequestArgs[0] not in ['upload-pack', 'receive-pack']:
                msg = "Git command argument '%s' is not supported." % self.sshRequestArgs[0]
                raise Exception, msg
        elif self.sshRequestCmd in ['git-upload-pack', 'git-receive-pack']:
            if len(self.sshRequestArgs) != 1:
                msg = "Git command '%s' needs one argument: %s" % (
                    self.sshRequestCmd, self.sshRequestArgs)
                raise Exception, msg
        else:
            msg = "Git command '%s' not supported." % self.sshRequestCmd
            raise Exception, msg

    def initActionName(self):
        self.actionName = 'Update'
        if self.sshRequestCmd == 'git':
            if self.sshRequestArgs[0] == 'upload-pack':
                self.actionName = 'Read'
        else:
            if self.sshRequestCmd == 'git-upload-pack':
                self.actionName = 'Read'

    def initUrlPath(self):
        if self.sshRequestCmd == 'git':
            self.urlPath = self.sshRequestArgs[1]
        else:
            self.urlPath = self.sshRequestArgs[0]

    def rewriteRequestArgs(self):
        if self.sshRequestCmd == 'git':
            self.sshRequestArgs[1] = self.servicePath
        else:
            self.sshRequestArgs[0] = self.servicePath

    def call(self):
        try:
            self.application.logger.info("Executing Git SSH command: %s" % self.shellCmd)
            self.application.logger.debug("Git client is authorised, so allowing unmediated communications on STDIN and STDOUT.")
            returnCode = call(self.shellCmd, shell=True)
            if returnCode < 0:
                raise Exception, "Git SSH command was terminated by signal: %s" % (returnCode)
            elif returnCode > 0:
                raise Exception, "Git SSH command exited with non-zero error code: %s" % (returnCode)
            self.application.logger.debug("Git SSH command executed OK")
        except OSError, inst:
            raise Exception, "Git SSH command execution failed: %s" % inst


class MercurialCommand(BaseCommand):

    def validateRequest(self):
        if self.sshRequestCmd != 'hg':
            msg = "Mercurial SSH command '%s' not supported." % self.sshRequestCmd
            raise Exception, msg
        if len(self.sshRequestArgs) != 4:
            msg = "Mercurial SSH command args look wrong (len): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[0] != '-R':
            msg = "Mercurial SSH command args look wrong (0): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[2] != 'serve':
            msg = "Mercurial SSH command args look wrong (2): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[3] != '--stdio':
            msg = "Mercurial SSH command args look wrong (3): %s" % self.sshRequestArgs
            raise Exception, msg

    def initActionName(self):
        self.actionName = 'Read'

    def initUrlPath(self):
        self.urlPath = self.sshRequestArgs[1]

    def rewriteRequestArgs(self):
        self.sshRequestArgs[1] = os.path.join(self.servicePath, 'repo')

    def call(self):
        canUpdate = self.isAccessAuthorised(actionName='Update')
        try:
            self.application.logger.info("Executing Mercurial SSH command: %s" % self.shellCmd)
            if canUpdate:
                self.application.logger.debug("Mercurial client has update permission, so allowing unmediated communications on STDIN and STDOUT.")
                stdin = sys.stdin
                inboundReader = None
            else:
                self.application.logger.debug("Client has no update permission, so filtering STDIN and allowing unmediated communications on STDOUT only.")
                stdin = PIPE
                inboundReader = ReadHgMessage
                validInboundPatterns = [
                    re.compile('^hello\n$'),
                    re.compile('^between'),
                    re.compile('^heads'),
                    re.compile('^changegroup'),
                    re.compile('^branches'),
                    # For cloning with hg v1.9.1.
                    re.compile('^batch'),
                    re.compile('^cmds'),
                    re.compile('^listkeys'),
                    re.compile('^namespace'),
                ]
            self.cmdproc = Popen(self.shellCmd, stdin=stdin, stdout=sys.stdout, shell=True)
            if inboundReader:
                inboundThread = PipeThread(name='inbound', stdin=sys.stdin, stdout=self.cmdproc.stdin, readerClass=inboundReader, logger=self.application.logger, validPatterns=validInboundPatterns, isDebug=self.isDebug)
                inboundThread.start()
            else:
                inboundThread = None
            self.application.logger.debug("Waiting for Mercurial SSH command to finish...")
            returnCode = self.cmdproc.wait()
            self.application.logger.debug("Mercurial SSH command finished.")
            if inboundThread:
                self.application.logger.debug("Joining on inbound thread....")
                inboundThread.join()
                self.application.logger.debug("Joined on inbound thread.")
            if returnCode == None:
                raise Exception, "Mercurial SSH command was still running. Pid: %s" % (self.cmdproc.pid)
            if returnCode < 0:
                raise Exception, "Mercurial SSH command was terminated by signal: %s" % (returnCode)
            elif returnCode > 0:
                raise Exception, "Mercurial SSH command exited with non-zero error code: %s" % (returnCode)
            elif inboundThread and inboundThread.error:
                if isinstance(inboundThread.error, AccessDenied):
                    raise AccessDenied, "Access denied by inbound thread: %s" % (inboundThread.error)
                else:
                    raise Exception, "Mercurial SSH inbound thread exited with error: %s" % (inboundThread.error)
            else:
                self.application.logger.info("Mercurial SSH command executed OK.")
        except OSError, inst:
            raise Exception, "Mercurial SSH command execution failed: %s" % inst


class SubversionCommand(BaseCommand):

    def validateRequest(self):
        if self.sshRequestCmd != 'svnserve':
            msg = "Subversion command '%s' not supported." % self.sshRequestCmd
            raise Exception, msg
        if len(self.sshRequestArgs) != 1:
            msg = "Subversion request args look wrong (len): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[0] != '-t':
            msg = "Subversion request args look wrong (0): %s" % self.sshRequestArgs
            raise Exception, msg

    def initActionName(self):
        self.actionName = 'Read'

    def initUrlPath(self):
        # Tease the requested service path from client.
        sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', 0)
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        # Send server greeting to the client.
        self.cmdproc = Popen('svnserve -t', stdin=PIPE, stdout=PIPE, shell=True)
        try:
            #self.application.logger.info("Reading svnserve greeting...")
            greeting = self.readServerMessage()
            #greeting = '( success ( 2 2 ( ) ( edit-pipeline svndiff1 absent-entries commit-revprops depth log-revprops partial-replay ) ) ) '
            self.sendClientMessage(greeting)
            self.application.logger.debug("Sent svnserve greeting to client: %s" % greeting)
        finally:
            self.cmdproc.stdin.close()
            self.cmdproc.wait()
        self.svnGreetingResponse = self.readClientMessage()
        self.application.logger.debug("Received greeting response from svn client: %s" % self.svnGreetingResponse)
        result = re.search('svn\+ssh://(\S*)\s', self.svnGreetingResponse)
        if not result:
            raise Exception, "Failed to tease service URL from Subversion client."
        self.serviceUrl = result.group().strip()
        #self.application.logger.debug("Teased out Subversion service URL: '%s'" % self.serviceUrl)
        serviceUrlParts = self.serviceUrl.split('/')
        self.urlPath = '/' + '/'.join(serviceUrlParts[3:5])
        self.urlNoPath = '/'.join(serviceUrlParts[:3])
        if not self.urlPath:
            raise Exception, "Failed to tease service URL path from Subversion client."
        self.application.logger.debug("Teased out Subversion service path: %s" % self.urlPath)

    def rewriteRequestArgs(self):
        self.sshRequestArgs.append('--tunnel-user')
        self.sshRequestArgs.append(self.person.name)
        self.sshRequestArgs.append('-r')
        self.sshRequestArgs.append(os.path.dirname(self.servicePath))

    def call(self):
        self.application.logger.info("Executing command via SSH: %s" % self.shellCmd)
        urlPatternString = '^\d+:' + self.urlNoPath.replace('+', '\\+').replace('.', '\\.')
        #self.application.logger.debug("URL pattern: %s" % urlPatternString)
        urlPattern = re.compile(urlPatternString)
        clientSideUrl = self.urlNoPath + self.urlPath
        serverSideUrl = self.urlNoPath + '/%s' % self.service.id
        #self.application.logger.debug("Client side: %s" % clientSideUrl)
        #self.application.logger.debug("Server side: %s" % serverSideUrl)
        inboundRewriter = UrlRewriter(urlPattern=urlPattern, oldUrl=clientSideUrl, newUrl=serverSideUrl, logger=self.application.logger)
        outboundRewriter = UrlRewriter(urlPattern=urlPattern, oldUrl=serverSideUrl, newUrl=clientSideUrl, logger=self.application.logger)
        canUpdate = self.isAccessAuthorised(actionName='Update')
        try:
            self.cmdproc = Popen(self.shellCmd, stdin=PIPE, stdout=PIPE, shell=True)
            # Inject messages to get things going again.
            # Discard greeting from the server (client has already seen it).
            self.readServerMessage()
            # Send greeting response from the server (we teased it from the client).
            greetingResponse = inboundRewriter.rewrite(self.svnGreetingResponse)
            self.sendServerMessage(greetingResponse)
            # Carry on with direct client-server communication.
            if canUpdate:
                validInboundPatterns = []
            else:
                validInboundPatterns = [
                    re.compile('^\(\ EXTERNAL .*'),
                    re.compile('^\(\ get-latest-rev .*'),
                    re.compile('^\(\ reparent .*'),
                    re.compile('^\(\ check-path.*'),
                    re.compile('^\(\ update .*'),
                    re.compile('^\(\ set-path .*'),
                    re.compile('^\(\ finish-report .*'),
                    re.compile('^\(\ success .*'),
                ]
            validOutboundPatterns = []
            inboundThread = PipeThread(name='Pipe inbound', stdin=sys.stdin, stdout=self.cmdproc.stdin, readerClass=ReadSvnMessage, logger=self.application.logger, rewriter=inboundRewriter, validPatterns=validInboundPatterns, isDebug=self.isDebug)
            outboundThread = PipeThread(name='Pipe outbound', stdin=self.cmdproc.stdout, stdout=sys.stdout, readerClass=ReadSvnMessage, logger=self.application.logger, rewriter=outboundRewriter, validPatterns=validOutboundPatterns, isDebug=self.isDebug, abortStdoutMessage='\n')
            inboundThread.start()
            outboundThread.start()
            #self.application.logger.info("Waiting for server to finish...")
            returnCode = self.cmdproc.wait()
            #self.application.logger.info("Server  finished...")
            #self.application.logger.info("Joining on threads....")
            outboundThread.join()
            #self.application.logger.info("Joined on Stdout thread.")
            inboundThread.join()
            #self.application.logger.info("Joined on Stdin thread.")
            if returnCode < 0:
                raise Exception, "Subversion SSH command was terminated by signal: %s" % (returnCode)
            elif returnCode > 0:
                raise Exception, "Subversion SSH command exited with non-zero error code: %s" % (returnCode)
            elif inboundThread.error:
                if isinstance(inboundThread.error, AccessDenied):
                    raise AccessDenied, "Access denied by inbound thread: %s" % (inboundThread.error)

                else:
                    raise Exception, "Subversion SSH inbound thread exited with error: %s" % (inboundThread.error)
            elif outboundThread.error:
                raise Exception, "Subversion SSH outbound thread exited with error: %s" % (outboundThread.error)
            else:
                self.application.logger.debug("Subversion SSH command executed OK")
        except OSError, inst:
            raise Exception, "Subversion SSH command execution failed: %s" % inst

    def readClientMessage(self):
        message = ReadSvnMessage(sys.stdin, self).read()
        #self.application.logger.debug("Received message from client: '%s'" % message)
        return message

    def sendClientMessage(self, message):
        #self.application.logger.debug("Sending message to client: '%s'" % message)
        sys.stdout.write(message)

    def readServerMessage(self):
        message = ReadSvnMessage(self.cmdproc.stdout, self).read()
        #self.application.logger.debug("Received message from server: '%s'" % message)
        return message

    def sendServerMessage(self, message):
        #self.application.logger.debug("Sending message to server: '%s'" % message)
        self.cmdproc.stdin.write(message)



class WriteBuffer(Thread):

    def __init__(self, pipe):
        Thread.__init__(self)
        self.queue = []
        self.isStopping = False
        self.pipe = pipe
        self.condition = Condition()

    def run(self):
        self.pipe.isDebug and self.pipe.log("Buffer running...", isDebug=True)
        chars = ''
        self.acquire()
        while not self.isStopping or len(self.queue):
            while not self.isStopping and not len(self.queue):
                self.wait()
            if len(self.queue):
                chars = ''.join(self.queue)
                self.queue = []
                self.release()
                self.output(chars)
                self.acquire()
        self.release()
        self.pipe.isDebug and self.pipe.log("Buffer stopping...", isDebug=True)

    def append(self, chars):
        #self.pipe.isDebug and self.pipe.log("Appending %s chars to buffer: %s" % (len(chars), repr(chars)), isDebug=True)
        self.acquire()
        self.queue.append(chars)
        self.notify()
        self.release()

    def acquire(self):
        #self.pipe.isDebug and self.pipe.log("Acquiring buffer lock...", isDebug=True)
        self.condition.acquire()

    def wait(self):
        #self.pipe.isDebug and self.pipe.log("Waiting for buffer notification...", isDebug=True)
        self.condition.wait()

    def notify(self):
        #self.pipe.isDebug and self.pipe.log("Notifying buffer...", isDebug=True)
        self.condition.notify()

    def release(self):
        #self.pipe.isDebug and self.pipe.log("Releasing buffer lock...", isDebug=True)
        self.condition.release()

    def output(self, chars):
        logchars = chars[:25] + (chars[25:] and '..')
        #self.pipe.isDebug and self.pipe.log("Outputting %s buffered chars: %s" % (len(chars), repr(logchars)), isDebug=True)
        self.pipe.log("Outputting %s buffered chars: %s" % (len(chars), repr(logchars)), isDebug=True)
        self.pipe.stdout.write(chars)
        self.pipe.stdout.flush()
        #time.sleep(0.01)  # Allow buffer to build up.

    def stop(self):
        #self.pipe.log("Buffer receiving stop signal...", isDebug=True)
        self.acquire()
        self.isStopping = True
        self.notify()
        self.release()
        #self.pipe.log("Buffer received stop signal.", isDebug=True)
    

class PipeThread(Thread):

    def __init__(self, name, stdin, stdout, readerClass, logger, rewriter=None, validPatterns=[], isDebug=False, abortStdoutMessage='', abortStderrMessage=''):
        Thread.__init__(self)
        self.name = name
        self.stdin = stdin
        self.stdout = stdout
        self.readerClass = readerClass
        self.logger = logger
        self.rewriter = rewriter
        self.validPatterns = validPatterns
        self.error = None
        self.isDebug = isDebug
        self.abortStdoutMessage = abortStdoutMessage
        self.abortStderrMessage = abortStderrMessage
        self.writeBuffer = WriteBuffer(self)
        self.lastMessageCondition = Condition()

    def run(self):
        self.log('Running...', isDebug=True)
        if self.writeBuffer:
            self.writeBuffer.start()
        try:
            while True:
                reader = self.readerClass(self.stdin, self)
                # Read message from stdin.
                message = reader.read()
                #self.isDebug and self.log("Received message with %s chars." % len(message), isDebug=True)
                if self.isDebug:
                    logchars = repr(message)
                    logchars = logchars[:60] + (logchars[60:] and '...')
                    self.log("Received message with %s chars: %s" % (len(message), logchars), isDebug=True)
                # Rewrite URLs.
                if self.rewriter:
                    message = self.rewriter.rewrite(message)
                if self.validPatterns:
                    isMessageValid = False
                    for validPattern in self.validPatterns:
                        if validPattern.match(message):
                            isMessageValid = True
                            break
                    if not isMessageValid:
                        msg = "Message is not allowed: %s" % (message)
                        self.log(msg)
                        raise AccessDenied, msg
                if self.writeBuffer:
                    if not self.writeBuffer.is_alive():
                        raise Exception, "Buffer thread is no longer active."
                    self.writeBuffer.append(message)
                else:
                    self.stdout.write(message)
                    self.stdout.flush()
        except EndOfFile:
            self.isDebug and self.log('End of file.', isDebug=True)
        except Exception, inst:
            self.error = inst
            self.log('Handling error: %s' % inst, isDebug=True)
            if self.abortStdoutMessage:
                self.isDebug and self.log('Writing abort message to stdout: %s' % repr(self.abortStdoutMessage), isDebug=True)
                if self.writeBuffer:
                    if self.writeBuffer.is_alive():
                        self.writeBuffer.append(self.abortStdoutMessage)
                else:
                    self.stdout.write(self.abortMessage)
                    self.stdout.flush()
            if self.abortStderrMessage:
                self.isDebug and self.log('Writing abort message to stderr: %s' % repr(self.abortStderrMessage), isDebug=True)
                sys.stderr.write(self.abortStderrMessage)
        finally:
            if self.writeBuffer:
                self.writeBuffer.stop()
                self.isDebug and self.log('Waiting for write buffer to stop...', isDebug=True)
                self.writeBuffer.join()
            self.isDebug and self.log('Closing thread\'s stdout.', isDebug=True)
            self.stdout.close()
            self.stdout = None
            self.stdin = None
            self.isDebug and self.log('Stopping.', isDebug=True)

    def log(self, line, isDebug=False, isError=False):
        line = "Pipe %s: %s" % (self.name, line)
        if isDebug:
            self.logger.debug(line)
        elif isError:
            self.logger.error(line)
        else:
            self.logger.info(line)


class BaseReader(object):

    def __init__(self, stdin, client):
        self.stdin = stdin
        self.client = client

    def log(self, line, isDebug=False, isError=False):
        if hasattr(self.client, 'log'):
            self.client.log(line, isDebug=isDebug, isError=isError)


class ReadSvnMessage(BaseReader):

    def read(self):
        hasMessage = False
        message = ''
        brackets = 0
        token = ''
        while not hasMessage:
            hasToken = False
            c = self.stdin.read(1)
            #self.log("Char: '%s' brackets: %s token: %s" % (c, brackets, token), isDebug=True)
            if c == '':
                raise EndOfFile
            token += c
            if token == '( ':
                hasToken = True
                brackets += 1
            elif token == ') ':
                hasToken = True
                brackets -= 1
            elif re.match('\d+:', token):
                octetCount = int(token.strip(':'))
                token += self.stdin.read(octetCount)
                hasToken = True
            elif re.match('\S+\s', token):
                hasToken = True
            elif re.match('\s', token):
                hasToken = True
            if hasToken:
                #self.log("Token: '%s'" % token, isDebug=True)
                message += token
                token = ''
                if not brackets:
                    hasMessage = True
                    #self.log("Message: '%s'" % message, isDebug=True)
        return message


class ReadHgMessage(BaseReader):

    characterCountPtn = re.compile('(.*\s)?(\d+)\n$')

    def read(self):
        hasMessage = False
        message = ''
        while not hasMessage:
            token = ''
            hasToken = False
            while not hasToken:
                char = self.stdin.read(1)
                #self.log("New char: %s" % repr(char), isDebug=True)
                if char == '':
                    # That's the end of the file.
                    if token or message:
                        raise Exception, "Premature end of file: chars not formed into message: %s" % (message + token)
                    else:
                        self.log("Raising EOF.", isDebug=True)
                        raise EndOfFile
                token += char
                if token in ['between\n', 'changegroup\n', 'branches\n', 'changegroupsubset\n', 'batch\n']:
                    # Wait for the next new line.
                    pass
                elif token.endswith('\n'):
                    # Let's call this a token.
                    hasToken = True
            #self.log("New token: '%s'" % token, isDebug=True)
            message += token
            if message in ['hello\n', 'between\n', 'heads\n', 'unbundle\n', 'branchmap\n', 'batch\n', 'listkeys\n']:
                # Simple command message so we're done.
                hasMessage = True
            elif self.characterCountPtn.search(token):
                # Read that amount of chars and we're done.
                length = self.characterCountPtn.search(token).group(2)
                length = int(length)
                chars = self.stdin.read(length)
                #self.log("New chars: %s" % (repr(chars)), isDebug=True)
                message += chars
                hasMessage = True
            else:
                # This is the inbound thread, so be defensive.
                msg = "Unknown mercurial message: %s" % repr(message)
                raise Exception, msg
            token = ''
        return message


#class ReadSingleChar(BaseReader):
#
#    def read(self):
#        message = ''
#        c = self.stdin.read(1)
#        if c == '':
#            raise EndOfFile
#        message = c
#        #self.log("Single char message: '%s'" % (c), isDebug=True)
#        return message


class UrlRewriter(object):

    def __init__(self, urlPattern, oldUrl, newUrl, logger):
        self.urlPattern = urlPattern
        self.oldUrl = oldUrl
        self.newUrl = newUrl
        self.logger = logger

    def rewrite(self, oldMessage):
        # Need to change octet count as well as string.
        newTokens = []
        oldTokens = self.tokenize(oldMessage)
        for oldToken in oldTokens:
            #self.log("Got token: %s" % oldToken)
            if self.urlPattern.match(oldToken):
                #self.log("Matched token: %s" % oldToken)
                newValue = oldToken.split(':', 1)[1].replace(self.oldUrl, self.newUrl)
                #self.log("Rewrote token: %s" % newToken)
                newLength = len(newValue)
                newToken = '%d:%s' % (newLength, newValue)
            else:
                newToken = oldToken
            newTokens.append(newToken)
        return ''.join(newTokens)

    def tokenize(self, message):
        message = list(message)
        tokens = []
        token = ''
        while message:
            hasToken = False
            c = message.pop(0)
            token += c
            if token == '( ':
                hasToken = True
            elif token == ') ':
                hasToken = True
            elif re.match('\d+:', token):
                octetCount = int(token.strip(':'))
                token += ''.join(message[:octetCount])
                message = message[octetCount:]
                hasToken = True
            elif re.match('\S+\s', token):
                hasToken = True
            elif re.match('\s', token):
                hasToken = True
            if hasToken:
                tokens.append(token)
                token = ''
        return tokens

    def log(self, line):
        self.logger.info("Rewriter: "+line)


class ServiceNotFound(Exception): pass

class EndOfFile(Exception): pass


