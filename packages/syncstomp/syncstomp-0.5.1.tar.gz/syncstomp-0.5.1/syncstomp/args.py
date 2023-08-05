from plumb_util.args import add_argparse_group as add_plumb_util_group, logger_from_args
from .json_wrap import Connection
from .managed import ManagedConnection

def add_argparse_group(parser):
    """Add a configuration group for syncstomp to an argparser"""
    add_plumb_util_group(parser)
    group = parser.add_argument_group('syncstomp', 'STOMP client configuration options')
    group.add_argument('-U', '--username', type=str, dest='username', default=None,
                        help='Username for the STOMP connection')
    group.add_argument('-W', '--password', type=str, dest='password', default=None,
                        help='Password for the STOMP connection')

def syncstomp_from_args(args, procname, managed=True):
    logger_from_args(args, procname)

    Cxn = ManagedConnection if managed else Connection
    stomp_connection = Cxn(zone=args.zone, user=args.username, passcode=args.password, version=1.1)
    stomp_connection.start()
    stomp_connection.connect(wait=True)

    return stomp_connection
