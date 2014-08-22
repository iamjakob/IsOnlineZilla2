import hashlib
from os import urandom
from base64 import b64encode, b64decode
from itertools import izip
import glob
import logging
import logging.handlers


# From https://github.com/mitsuhiko/python-pbkdf2
from pbkdf2 import pbkdf2_bin


# Parameters to PBKDF2. Only affect new passwords.
SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
# Linear to the hashing time. Adjust to be high but take a reasonable
# amount of time on your server. Measure with:
# python -m timeit -s 'import passwords as p' 'p.make_hash("something")'
COST_FACTOR = 10000

# --------- THE LOG ----------------
LOG_FILENAME = 'the_log.log'
mylogger = logging.getLogger('TheLogger')
mylogger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

t_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                 maxBytes=2550,
                                                 backupCount=1,
                                                 )
t_handler.setFormatter(formatter)
mylogger.addHandler(t_handler)


LEVELS = { 'debug':logging.DEBUG,
           'info':logging.INFO,
           'warning':logging.WARNING,
           'error':logging.ERROR,
           'critical':logging.CRITICAL,
           }

def make_hash(password):
    """Generate a random salt and return a new hash for the password."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    salt = b64encode(urandom(SALT_LENGTH))
    return 'PBKDF2${}${}${}${}'.format(
        HASH_FUNCTION,
        COST_FACTOR,
        salt,
        b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                             getattr(hashlib, HASH_FUNCTION))))


def check_hash(password, hash_):
    """Check a password against an existing hash."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
    assert algorithm == 'PBKDF2'
    hash_a = b64decode(hash_a)
    hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                        getattr(hashlib, hash_function))
    assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
    # Same as "return hash_a == hash_b" but takes a constant time.
    # See http://carlos.bueno.org/2011/10/timing.html
    diff = 0
    for char_a, char_b in izip(hash_a, hash_b):
        diff |= ord(char_a) ^ ord(char_b)
    return diff == 0

class bcolors:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class ColorLog:
    debug = True

    def __init__(self, debug):
        self.debug = debug

    def header(self, s):

        if self.debug:
            print bcolors.HEADER + s + bcolors.ENDC
        else:
            pass

    def blue(self, s):

        if self.debug:
            print bcolors.OKBLUE + s + bcolors.ENDC
        else:
            pass

    def green(self, s):

        if self.debug:
            print bcolors.OKGREEN + s + bcolors.ENDC
        else:
            pass

    def warning(self, s):

        if self.debug:
            print bcolors.WARNING + s + bcolors.ENDC
        else:
            pass

    def fail(self, s):

        if self.debug:
            print bcolors.FAIL + s + bcolors.ENDC
        else:
            pass



colorlog = ColorLog(debug=True)
