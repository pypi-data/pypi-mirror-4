import os
import pwd


def getlogin():
    """avoid usinng os.getlogin() because of strange tty / stdin problems
    (man 3 getlogin)
    Another solution would be to use $LOGNAME, $USER or $USERNAME
    """
    return pwd.getpwuid(os.getuid())[0]


def update_parser(parser):
    login = getlogin()
    parser.add_option('-u', '--dbuser', dest='dbuser', action='store',
                      default=login, help="database user")
    parser.add_option('-w', '--dbpassword', dest='dbpassword', action='store',
                      default=login, help="database name")
    parser.add_option('-n', '--dbname', dest='dbname', action='store',
                      default=None, help="database name")
    parser.add_option('--euser', dest='euser', action='store',
                      default=login, help="esuer name")
    parser.add_option('--epassword', dest='epassword', action='store',
                      default=login, help="euser's password' name")
    parser.add_option('--sourccubes.file', dest='source', action='store',
                      default=None, help="a source's config file (ignore other db options in this case)")
    return parser
