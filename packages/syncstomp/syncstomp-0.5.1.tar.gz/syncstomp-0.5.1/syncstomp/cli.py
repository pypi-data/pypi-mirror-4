from stomp.cli import stomppy_version, StompCLI as RawStompCLI
from stomp.exception import ConnectFailedException
from argparse import ArgumentParser
from plumb_util import find_service
from pprint import pformat
from .args import add_argparse_group, logger_from_args

syncstomp_version = "syncstomp wrap of " + stomppy_version


class StompCLI(RawStompCLI):
    def __init__(self, *args, **kwargs):
        self._headers = {}
        super(StompCLI,self).__init__(*args, **kwargs)

    def do_headers(self, args):
        if len(args) == 0:
            self.__sysout('Current headers:\n' + pformat(self._headers, 1))
            return
        else:
            self.__error('Expecting: headers')
            return

    def help_headers(self):
        self.help('headers', 'Display current message transmission headers.')

    def do_header(self, args):
        arglist = args.split()
        if len(arglist) == 0 or len(arglist) > 2:
            self.__error('Expecting: header <header> [<value>]')
        elif len(arglist) == 1:
            if arglist[0] not in self._headers:
                self.__error('Header %s was not set' % arglist[0])
            else:
                self._headers.pop(arglist[0])
                self.__sysout('Header %s cleared' % arglist[0])
        elif len(arglist) == 2:
            self._headers[arglist[0]] = arglist[1]
            self.__sysout('Header %s set to "%s"' % (arglist[0], arglist[1]))

    def help_header(self):
        self.help('header <header> [<value>]', 'Clear header <header> or set its value to <value>.')

    def do_send(self, args):
        args = args.split()
        if len(args) < 2:
            self.__error('Expecting: send <destination> <message>')
        elif not self.transaction_id:
            self.conn.send(destination=args[0], message=' '.join(args[1:]), **self._headers)
        else:
            self.conn.send(destination=args[0], message=' '.join(args[1:]), transaction=self.transaction_id, **self._headers)


def main():
    parser = ArgumentParser(version=syncstomp_version)
    add_argparse_group(parser)

    parser.add_argument('-F', '--file', type = str, dest = 'filename',
                        help = 'File containing commands to be executed, instead of prompting from the command prompt.')
    parser.add_argument('-S', '--stomp', type = float, dest = 'stomp', default = 1.0,
                        help = 'Set the STOMP protocol version.')

    parser.set_defaults()
    args = parser.parse_args()
    logger = logger_from_args(args, 'stomp')

    # Use service autodiscovery
    servers = find_service('_stomp._tcp', args.zone)

    # Try to connect
    connected = False
    while not connected:
        if len(servers) == 0:
            logger.error("No servers left to try.")
            exit(1)
        (host, port) = servers.pop(0)
        logger.info("Trying %s port %d" % (host, port))

        try:
            st = StompCLI(host, port, args.username, args.password, args.stomp)
            connected = True
        except ConnectFailedException:
            pass
    
    if args.filename:
        st.do_run(args.filename)
    else:
        try:
            try:
                st.cmdloop()
            except KeyboardInterrupt:
                pass
        finally:
            st.onecmd('disconnect')

if __name__ == '__main__':
    main()
