#!/usr/bin/python

import SocketServer
import sys, os, socket

class FTPsession(SocketServer.BaseRequestHandler):
    """One FTP Session from login to exit"""
    
    block_size=65535
    
    def setup(self):
        self.data_socket=None
        try:
            self.options=self.server.options
        except:
            self.options={}

        self.root=os.path.abspath(self.options.get('root', os.getcwd()))
        self.user=self.options.get('user', None)
        self.password=self.options.get('password', None)
        self.debug=self.options.get('debug', None)
        # no password

    def abs_path(self, path):
        path=os.path.abspath(os.join(self.root_dir, path))

    def response(self, st):
        """Send a response to the client"""
        if self.debug:
            print 'response', st
        self.request.send("%s\r\n" % (st,) )

    def cmd_quit(self, args):
        self.response("221 Have a good one!")
        raise SystemExit
    
    def cmd_user(self, args):
        if args[0] != self.user:
            self.response("502 Invalid user")
        else:
            self.response("331 User name ok")
    
    def cmd_pass(self, args):
        if self.password and args[0]!=self.password:
            self.response("530 Not logged in")
        else:
            self.response("230 User logged in")
    
    def cmd_dummy(self, args):
        self.response("200 OK ignored")
    
    cmd_rein=cmd_dummy
    cmd_type=cmd_dummy
    cmd_noop=cmd_dummy
    cmd_cwd=cmd_dummy
    cmd_allo=cmd_dummy
    
    def cmd_syst(self, args):
        self.response("215 MKSBackup ftp")

    def cmd_port(self, args):
        try:
            parts=args[0].split(',')
            if self.data_socket:
                self.data_socket.close()
                self.datas_ocket=None
            port=int(parts[4])*256 + int(parts[5])
            host='.'.join(parts[0:4])
            self.data_socket=socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.connect((host, port))
        except IndexError:
            self.response('500 port error')
            raise
        else:
            self.response('200 %s:%d' % (host, port))

    def cmd_pasv(self, args):
        if self.data_socket:
            self.data_socket.close()
            self.datas_ocket=None
        
        local_ip=self.request.getsockname()[0]
        
        self.data_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.bind((local_ip, 0))
        
        self.data_socket.listen(1) 
        
        port=self.data_socket.getsockname()[1]
        self.response('227 Entering passive mode (%s,%d,%d).' % (
                                local_ip.replace('.', ','), port / 256, port % 256))

        conn, addr=self.data_socket.accept()
        self.data_socket.close()
        self.data_socket=conn

    def cmd_list(self, args):
        if args:
            dirname=args[0]
        else:
            dirname="."
        # should check if can access the dirname
        lst = os.listdir(self.root)
        
        if lst is not None:
            self.response("150 opening ASCII connection for file list")
            data="\r\n".join(lst+[''])
            self.data_socket.send(data)
            self.data_socket.close()
            self.response("226 transfer complete")
        else:
            self.response("553 outside base directory of server")

    def cmd_size(self, args):
        self.response("550 not implemented")
    
    def cmd_cdup(self, args):
        self.response("553 already at the root dir")
    
    def cmd_mkd(self, args):
        target=os.path.join(self.root, args[0])
        if not os.path.isdir(target):
            try:
                os.mkdir(target)
            except OSError, e:
                self.response('521 "%s" %s' % (args[0], e,))
            else:
                self.response('257 "%s" directory created' % (args[0], ))
        else:
            self.response('521 "%s" directory already exists' % (args[0], ))
            
    def cmd_retr(self, args):
        if not args:
            self.response("500 retr syntax error")

        filename=args[0]
        if not os.path.isfile(filename):
            self.response("553 filename not found")

        filein=open(filename, 'rb')
        data=filein.read(self.block_size)
        self.response("125 Transfer started")
        while data:
            self.data_socket.send(data)
            data=filein.read(self.block_size)

        self.response("226 Closing data connection")
        self.data_socket.close()
        self.data_socket = None

    def cmd_stor(self, args):
        if not args:
            self.response("500 stor syntax error")
            return

        filename=os.path.abspath(os.path.join(self.root, args[0].lstrip('/')))
        if os.path.isdir(filename):
            self.response("553 target file is a directory")
            return

        if not filename.startswith(self.root):
            self.response("553 File name not allowed")
            return
            
        dirname=os.path.dirname(filename)
        if not os.path.isdir(dirname):
            try:
                os.makedirs(dirname)
            except Exception:
                self.response("553 directory don't exists")

            
        #mode = ['w','wb'][self.binary]
        try:
            fileout=open(filename, 'wb')
            self.response("125 Data transfer starting")
            try:
                while 1:
                    data=self.data_socket.recv(self.block_size)
                    if not data: 
                        break
                    fileout.write(data)
            except:
                raise
                pass
            fileout.close()
            self.response("226 Transfer complete.")
        except:
            self.response("451 local error")
            raise

    def cmd_dele(self, args):
        self.response("502 DELE not implemented")
            
    def handle(self):
        self.peername = self.request.getpeername()
        self.response("220 MKSBackup ftp ready")
        while 1:
            cmd_line=''
            while cmd_line.find('\n')==-1:
                data=self.request.recv(1024)
                if not data:
                    break
                cmd_line+=data
                
            if self.debug:
                print 'request from', self.peername, cmd_line

            if (not cmd_line): 
                break
            cmd_line=cmd_line.rstrip()
            cmd_args=cmd_line.split(' ', 1) # !!! handle only one arg !
            cmd=cmd_args[0].lower()
            
            if cmd == "quit":
                self.response("221 OK, bye")
                break

            try:
                method=getattr(self, 'cmd_'+cmd)
            except AttributeError:
                self.response("502 %s not implemented" % (cmd, ))
            else:
                try:
                    method(cmd_args[1:])
                except:
                    self.response("451 local error")
                    raise

class FTPserver(SocketServer.ThreadingTCPServer):    
    
    allow_reuse_address = True
    daemon_threads = True
    
    def __init__(self, addr=('',0), handler=FTPsession, **options):
        self.options = options
        allowed=self.options.get('allowed','')
        if allowed:
            self.allowed=map(socket.gethostbyname, allowed.split(','))
        else:
            self.allowed=[]
                   
        SocketServer.ThreadingTCPServer.__init__(self, addr, handler)

    def verify_request(self, reqsocket, client_address):
        return not self.allowed or client_address[0] in self.allowed

def ftpmain(argv):
    from optparse import OptionParser

    parser=parser=OptionParser(version='%%prog')
    parser.set_usage('%prog [options]\n\n')
    
    parser.add_option("-P", "--port", dest="port", default='21', help="listen on port", metavar="PORT")
    parser.add_option("-r", "--root", dest="root", default='/', help="root directory", metavar="DIR")
    parser.add_option("-u", "--user", dest="user", default='ftp', help="unique user", metavar="USER")
    parser.add_option("-p", "--password", dest="password", default=None, help="user password", metavar="PASSWORD")
    parser.add_option("-1", "--once", dest="once", action="store_true", default=False, help="serve only one request")
    parser.add_option("-a", "--allowed", dest="allowed", default='', help="comma separated list of host allowed to connect", metavar="HOST_LIST")
    parser.add_option("-b", "--bind", dest="bind", default='', help="bind to a specific address", metavar="address")
    
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="display debugging")
    
    cmd_options, cmd_args=parser.parse_args(argv)

    server=FTPserver(addr=('',int(cmd_options.port)), handler=FTPsession, root=cmd_options.root, user=cmd_options.user, password=cmd_options.password, allowed=cmd_options.allowed, debug=cmd_options.debug)

    print 'ftp server listening on', server.socket.getsockname()
    print 'user is "%s"' % (cmd_options.user, )
    if not cmd_options.password:
        print 'password is <empty>'
    else:
        print 'password is "%s"' % (cmd_options.password, )

    if cmd_options.once:
        server.handle_request()
    else:
        server.serve_forever()
    
if __name__ == '__main__':

    ftpmain(sys.argv)
