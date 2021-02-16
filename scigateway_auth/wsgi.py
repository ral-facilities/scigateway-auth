import logging
import sys
logging.basicConfig(stream=sys.stderr)

from scigateway_auth.app import app as application
