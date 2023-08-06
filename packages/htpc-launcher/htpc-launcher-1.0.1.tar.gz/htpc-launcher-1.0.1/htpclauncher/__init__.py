APP_NAME = 'HTPC Launcher'
PROJECT_NAME = 'htpc-launcher'

VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_RELEASE = 1

VERSION_SHORT = '%d.%d' % (VERSION_MAJOR, VERSION_MINOR)
VERSION = '%s.%d' % (VERSION_SHORT, VERSION_RELEASE)

LAUNCH_SCRIPT = 'htpc-launcher'
DEFAULT_CONF_FILE = '~/.htpc-launcher.conf'
DEFAULT_LOG_FILE = '~/.htpc-launcher.log'

from app import IrSwitchApp

