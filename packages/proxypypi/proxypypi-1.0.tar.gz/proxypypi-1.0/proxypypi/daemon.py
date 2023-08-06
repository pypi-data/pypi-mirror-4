import os, signal, sys, logging, time, errno
import fcntl


pid_fd = -1


class NonFatalException(Exception):
    '''This exception should be raised by daemon processing code
    that must return to the top-level processing loop.
    '''


class FatalException(Exception):
    '''This exception should be raised in any situation where the
    state of the daemon has become unworkable and it must exit.
    '''


class Daemon(object):
    def __init__(self, should_separate=True, pid_file='',
            console_out_file='/dev/null'):
        self.should_separate = should_separate
        self.pid_file = pid_file
        self.console_out_file = console_out_file

    should_exit = 0
    handle_signals = True

    # this will be set to a list if we actually spawn any children
    children = None

    def separate(self):
        '''Separate the daemon from its parent process.

        - make sure the sys.std(in|out|err) are completely cut off
        - make our parent PID 1

        Write our new PID to the pid_file.

        From A.M. Kuchling (possibly originally Greg Ward) with
        modification from Oren Tirosh, and finally a small mod from me.
        '''
        global pid_fd
        if not self.should_separate:
            return

        # don't attempt this if the PIDFILE isn't set
        if not self.pid_file:
            return

        #
        # first check there isn't an old daemon still running
        # before we clobber the pid file, and exit if it is,
        # in the *main* process, so our caller knows we're useless.
        #
        pid_fd = os.open(self.pid_file, os.O_RDWR|os.O_CREAT, 0644)
        try:
            fcntl.flock(pid_fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except IOError, (err, strerr):
            if err == errno.EAGAIN:
                logging.error("%s lock busy; old daemon still running" %
                        self.pid_file)
                sys.exit(1)
            loging.error("Can't flock %s: %s" % (self.pid_file, strerr))
            sys.exit(1)

        #
        # release lock as child can't inherit lock on Solaris,
        # as python flock on Solaris is implemented using (stupid SysV)
        # fcntl F_SETLK.
        #
        os.close(pid_fd)

        # Fork once
        if os.fork() != 0:
            os._exit(0)

        # Create new session
        os.setsid()
        pid = os.fork()
        if pid:
            logging.info('%s running as PID %s' % (self.__class__.__name__,
                pid))
            os._exit(0)

        os.chdir("/")
        os.umask(022)

        # close off sys.std(in|out|err), redirect to a "console output
        # file" (default /dev/null) so the file descriptors can't be used again
        infile = os.open('/dev/null', os.O_RDONLY)
        os.dup2(infile, 0)
        outfile = os.open(self.console_out_file, os.O_WRONLY | os.O_CREAT |
            os.O_APPEND)
        os.dup2(outfile, 1)
        os.dup2(outfile, 2)
        if infile > 2:
            os.close(infile)
        if outfile > 2:
            os.close(outfile)

        if self.handle_signals:
            # set our signal handlers
            signal.signal(signal.SIGHUP, self.handleSIGHUP)
            signal.signal(signal.SIGTERM, self.handleSIGTERM)

        #
        # Reopen pid file as child and maintain lock for life of daemon
        # (as parent lock can't be passed to child)
        # If somebody else locks it between the above LOCK_EX and this
        # one then we just give up.
        #
        pid_fd = os.open(self.pid_file, os.O_RDWR|os.O_CREAT, 0644)
        try:
            fcntl.flock(pid_fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except IOError, (err, strerr):
            if err == errno.EAGAIN:
                logging.error("%s lock busy, when reopening" % self.pid_file)
                sys.exit(1)
            loging.error("Can't re-flock %s in child: %s" % (self.pid_file,
                strerr))
            sys.exit(1)

        #
        # write pid
        #
        os.ftruncate(pid_fd, 0)
        if hasattr(os, 'SEEK_SET'):
            os.lseek(pid_fd, 0, os.SEEK_SET)
        else:
            # pre py2.5 compat
            os.lseek(pid_fd, 0, 0)
        os.write(pid_fd, str(os.getpid()) + '\n')
        # ...and leave (global) pid_fd open!

        os.write(1, '\nDaemon started: %s\n' % time.ctime())

    def handleSIGHUP(self, num, stack):
        ''' Handle the HUP signal.
        '''
        logging.debug('%s PID=%s received SIGHUP', self.__class__.__name__,
            self.getpid())

    def handleSIGTERM(self, num, stack):
        ''' Handle the TERM signal.

            The default action is to set a flag indicating that the next
            main loop should exit.
        '''
        logging.debug('%s received SIGTERM', self.__class__.__name__)

        if self.should_exit:
            logging.error('%s received 2 SIGTERM without exiting, forcing '
                'exit now', self.__class__.__name__)
            raise SystemExit

        logging.info('%s received interrupt, will exit when current ' +
                 'processing finishes...', self.__class__.__name__)
        self.should_exit = 1

    def start(self):
        '''The daemon has just been started; do things if necessary.

        This method should be used instead of putting code in __init__ as
        that code will be executed even if the daemon is not being started
        (ie. if it's being checked or stopped).
        '''
        pass

    def main(self):
        self.separate()
        self.start()
        logging.info('%s running...', self.__class__.__name__)
        while not self.should_exit:
            try:
                self.process()
            except KeyboardInterrupt:
                self.handleSIGTERM(None, None)
            except NonFatalException:
                logging.exception("%s uncaught non-fatal error",
                    self.__class__.__name__)
            except FatalException:
                logging.critical("%s daemon had FATAL ERROR",
                    self.__class__.__name__)
                break
            except Exception:
                logging.exception("%s daemon had FATAL ERROR",
                    self.__class__.__name__)
                break
            except BaseException, e:
                # all remaining exceptions
                logging.info("%s exception %s raised",
                    self.__class__.__name__, e)
                break

        logging.info('%s exiting', self.__class__.__name__)
        try:
            self.cleanup()
        except Exception:
            logging.exception("%s daemon failed to clean up",
                self.__class__.__name__)
        except BaseException, e:
            logging.error("%s exception %s raised during cleanup",
                self.__class__.__name__, e)

    def process(self):
        '''Executed once per loop in main().

        Override to provide your application's functionality.

        *Warning*: unless this function performs a time.sleep() or select()
        or similar it will be called continuously.
        '''
        raise NotImplementedError

    def cleanup(self):
        '''Executed as the daemon is exiting.

        Default behaviour is to do nothing.
        '''
        pass

    def control(self, command):
        '''Interface to manage a daemon.

        '''
        help = '''%s: control a daemon

        The currently-active process is identified by the contents of:

          %s

        Available commands:
            "run"           run in the foreground
            "start"         start the daemon - run self.main()
            "stop"          stop the active process
            "restart"       stop & start the active process
            "forcerestart"  forcibly stop & start the active process
            "condstart"     start the daemon if it's not running
            "maybestop"     stop the active process only if it's running
            "status"        display the status of the active process
        '''
        pidfile = self.pid_file or '<undefined>'
        if command == 'help':
            print help%(sys.argv[0], pidfile)
            return
        if command == 'status':
            self.status()
            return
        if command == 'run':
            self.should_separate = False
            command = 'start'
        elif command in ('stop', 'maybestop', 'restart', 'forcerestart'):
            # stop() will sys.exit() if there's a problem
            self.stop(command)
            if 'restart' in command:
                command = 'start'
            else:
                return
        elif command == 'condstart':
            if self.is_running():
                return
            else:
                command = 'start'
        if command == 'start':
            print '%s starting...'%sys.argv[0]
            self.main()
        else:
            sys.exit('Invalid command %r\n'%(command,) +
                help%(sys.argv[0], pidfile))

    def get_pid(self):
        '''Get the process ID from self.pid_file.

        BWEARE: this code will sys.exit() if there's a problem!
                (this is the most convenient behavior)
        '''
        if not self.pid_file:
            sys.exit('cannot run process control with no pid_file')
        if not os.path.exists(self.pid_file):
            print 'no PID file for %s'%sys.argv[0]
            return

        # get the PID
        try:
            return int(open(self.pid_file).read())
        except ValueError:
            sys.exit('PID file %s contains garbage' % self.pid_file)

    def is_running(self):
        '''Determine the status of the currently running process for this
        daemon.

        The PID is identified by self.pid_file.
        '''
        pid = self.get_pid()
        if not pid:
            return False

        # send it a "hi there!"
        try:
            os.kill(pid, 0)
        except OSError, e:
            if e.errno == errno.ESRCH:
                return False
            else:
                sys.exit('%s (pid %s) is not running (%s)'%(sys.argv[0],
                    pid, e))
        return True

    def status(self):
        '''Determine the status of the currently running process for this
        daemon.

        The PID is identified by self.pid_file.
        '''
        if self.is_running():
            pid = self.get_pid()
            # XXX extend this test one day to hit HTTP using
            # config['web_address'] / status to make sure it's actually all OK
            print '%s (pid %s) is running'%(sys.argv[0], pid)
        else:
            print '%s is not running'%sys.argv[0]

    def stop(self, command='stop'):
        '''Stop the currently running process for this daemon.

        The PID is identified by self.pid_file.
        '''
        pid = self.get_pid()
        if not pid:
            return

        # send it a TERM
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError, e:
            if e.errno == errno.ESRCH and ('restart' in command
                    or command == 'maybestop'):
                # all good
                print '%s (pid %s) is not running'%(sys.argv[0], pid)
                return
            sys.exit('%s (pid %s) could not be stopped (%s)'%(sys.argv[0],
                pid, e))

        # wait to see if that killed the process
        print 'sending pid %s SIGTERM'%pid,
        sys.stdout.flush()
        for i in range(10):
            time.sleep(.5)
            try:
                os.kill(pid, 0)
            except OSError, e:
                if e.errno == errno.ESRCH:
                    print 'stopped'
                    return
                raise
            print '.',
            sys.stdout.flush()

        if 'force' in command:
            sys.stderr.write('\nstill running; sending SIGKILL\n')
            sig = signal.SIGKILL
        else:
            # some processes (eg. smsd) respond to a second TERM
            sys.stderr.write('\nstill running; sending second SIGTERM\n')
            sig = signal.SIGTERM

        # 5 seconds later the process is still running, try harder
        try:
            os.kill(pid, sig)
        except OSError, e:
            if e.errno == errno.ESRCH:
                # race condition
                print 'stopped'
                return
            sys.exit('\n%s (pid %s) could not be stopped (%s)'%(
                sys.argv[0], pid, e))

        # a little grace time for exit/cleanups
        time.sleep(.5)


if __name__ == '__main__':
    class Test(Daemon):
        def start(self):
            logging.basicConfig(filename='/tmp/daemon-test.log',
                level=logging.DEBUG)

        def process(self):
            logging.debug('process should_exit=%s'%self.should_exit)

    Test(pid_file='/tmp/daemon-test.pid').control(sys.argv[1])

#
# Copyright (c) 2013, ekit.com Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
