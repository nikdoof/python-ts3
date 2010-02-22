class ConnectionError():

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__():
        return 'Error connecting to host %s port %s' % (self.ip, self.port)

ts3_escape = { '/': r"\/",
               ' ': r'\s',
               '|': r'\p',
               "\a": r'\a',
               "\b": r'\b',
               "\f": r'\f',
               "\n": r'\n',
               "\r": r'\r',
               "\t": r'\t',
               "\v": r'\v' }
               

class TS3Proto():

    bytesin = 0
    bytesout = 0

    _connected = False

    def __init__(self):
        pass

    def connect(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOC_STREAM)
        try:
            s.connect(ip, port)
        except:
            raise ConnectionError(ip, port)
        else:
            self._sock = s

        while true:
            data =+ self._sock.recv(4096)
            if not data: break
        
        if data.strip() == "TS3":
            self._connected = True

    def disconnect(self):
        self.send_command("quit")
        self._sock.disconnect()
        self._connected = False

    def send_command(self, command, keys=None, opts=None):
        cmd = self.construct_command(command, keys=keys, opts=opts)

        if self._connected == True:
            self._sock.send(cmd)
            

    def send_recv_command(self, command, keys=None, opts=None):
        self.send_command(command, keys, opts)

        data = self._sock.recv(1024)
        while len(data):
            resp = resp + data
            data = self._sock.recv(1024)

        return self.parse_command(resp)

    def construct_command(self, command, keys=None, opts=None):
        """
        Constructs a TS3 formatted command string

        Keys can have a single nested list to construct a nested parameter

        @param command: Command list
        @type command: string
        @param keys: Key/Value pairs
        @type keys: dict
        @param opts: Options
        @type opts: list
        """

        cstr = []
        cstr.append(command)

        # Add the keys and values, escape as needed        
        if keys:
            for key in keys:
                if isinstance(keys[key], list):
                    ncstr = []
                    for nest in keys[key]:
                        ncstr.append("%s=%s" % (key, self._escape_str(nest)))
                    cstr.append("|".join(ncstr))
                else:
                    cstr.append("%s=%s" % (key, self._escape_str(keys[key])))

        # Add in options
        if opts:
            for opt in opts:
                cstr.append("-%s" % opt)

        return " ".join(cstr)

    def parse_command(self, commandstr):
        """
        Parses a TS3 command string into command/keys/opts tuple

        @param commandstr: Command string
        @type commandstr: string
        """

        cmdlist = commandstr.split(' ')

        command = cmdlist[0]
        keys = {}
        opts = []

        for key in cmdlist[1:]:
            if len(key.split('|')) > 1:
                output = []
                # Nested Keys
                nkeys = key.split('|')
                for nkey in nkeys:
                    nvalue = nkey.split('=')
                    okey = nvalue[0]
                    output.append(nvalue[1])
                keys[okey] = output
                continue
            if len(key.split('=')) > 1:
                # Key value
                nvalue = key.split('=')
                keys[nvalue[0]] = self._unescape_str(nvalue[1])
                continue
            elif key[0] == '-':
                opts.append(key[1:])
                continue

        return (command, keys, opts)
         

    @staticmethod
    def _escape_str(value):
        """
        Escape a value into a TS3 compatible string

        @param value: Value
        @type value: string/int

        """

        if isinstance(value, int): return "%d" % value
        value = value.replace("\\", r'\\')
        for i, j in ts3_escape.iteritems():
            value = value.replace(i, j)
        return value

    @staticmethod
    def _unescape_str(value):
        """
        Unescape a TS3 compatible string into a normal string

        @param value: Value
        @type value: string/int

        """

        if isinstance(value, int): return "%d" % value
        value = value.replace(r"\\", "\\")
        for i, j in ts3_escape.iteritems():
            value = value.replace(j, i)
        return value


    def send(self, payload):
        if self._connected:
            self._socket.send(payload)


class TS3Server(TS3Proto):
    def __init__(self, ip, port):
        """
        Abstraction class for TS3 Servers

        @param ip: IP Address
        @type ip: str
        @param port: Port Number
        @type port: int

        """
        self.connect(ip, port)


if __name__ == '__main__':
    p = TS3Proto()

    #print p.construct_command("serverlist")
    #print p.construct_command("clientlist", opts=['uid', 'away', 'groups'])
    #print p.construct_command("command", keys={'arg1': 'val1'}, opts=['opt1', 'opt2'])
    #print p.parse_command(p.construct_command("command", keys={'arg1': 'val1'}, opts=['opt1', 'opt2']))

    #print p.construct_command("clientkick", keys={'clid': [1,2,3], 'reasonid': 5, 'reasonmsg': 'Go Away!'})
    print p.parse_command(p.construct_command("clientkick", keys={'clid': [1,2,3], 'reasonid': 5, 'reasonmsg': 'Go Away!'}))

    #for bob in ts3_escape:
    #    print bob, ts3_escape[bob]
