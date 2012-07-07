#!/usr/bin/env ipython
from chipcon_nic import *

class RfCat(FHSSNIC):
    def RFdump(self, msg="Receiving", maxnum=100, timeoutms=1000):
        try:
            for x in xrange(maxnum):
                y, t = self.RFrecv(timeoutms)
                print "(%5.3f) %s:  %s" % (t, msg, y.encode('hex'))
        except ChipconUsbTimeoutException:
            pass

    def scan(self, basefreq=902e6, inc=250e3, count=104, delaysec=2, drate=38400, lowball=1):
        '''
        scan for signal over a range of frequencies
        '''
        self.RFdump("Clearing")
        self.lowball(lowball)
        self.setMdmDRate(drate)
        print "Scanning range: "
        while not keystop():
            print
            for freq in xrange(int(basefreq), int(basefreq+(inc*count)), int(inc)):
                print "Scanning for frequency %d..." % freq
                self.setFreq(freq)
                self.RFdump(timeoutms=delaysec*1000)
                if keystop():
                    break

        self.lowballRestore()

    def rf_configure(*args, **k2args):
        pass

    def rf_redirection(self, fdtup):
        if len(fdtup)>1:
            fd0i, fd0o = fdtup 
        else:
            fd0i, = fdtup 
            fd0o, = fdtup 

        fdsock = False      # socket or fileio?
        if hasattr(fd0i, 'recv'):
            fdsock = True

        while True:
            x,y,z = select.select([fd0i ], [], [], .1)
            #if self._pause:
            #    continue

            if fd0i in x:
                if fdsock:
                    data = fd0i.recv(self.max_packet_size)
                else:
                    data = fd0i.read(self.max_packet_size)

                if not len(data):       # terminated socket
                    break

                self.RFxmit(data)

            try:
                data = self.RFrecv(0)
                if fdsock:
                    fd0o.sendall(data)
                else:
                    fd0o.write(data)
            except ChipconUsbTimeoutException:
                pass


def interactive(idx=0, DongleClass=RfCat, intro=''):
    import rflib.chipcon_nic as rfnic

    d = DongleClass(idx=idx)

    gbls = globals()
    lcls = locals()

    try:
        import IPython.Shell
        ipsh = IPython.Shell.IPShell(argv=sys.argv, user_ns=lcls, user_global_ns=gbls)
        print intro
        ipsh.mainloop(intro)

    except ImportError, e:
        try:
            from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell
            ipsh = TerminalInteractiveShell()
            ipsh.user_global_ns.update(globals())
            ipsh.user_global_ns.update(locals())
            ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
            ipsh.mainloop(intro)
        except ImportError, e:
            print e
            shell = code.InteractiveConsole(gbls)
            shell.interact(intro)


if __name__ == "__main__":
    idx = 0
    if len(sys.argv) > 1:
        idx = int(sys.argv.pop())

    interactive(idx)
