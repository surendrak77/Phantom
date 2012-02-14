import os
from pyhantom.authz.cumulus_sqlalch import CumulusDataStore
from pyhantom.authz.simple_file import SimpleFileDataStore
from pyhantom.phantom_exceptions import PhantomAWSException
import logging
import dashi.bootstrap
from pyhantom.system.epu_local_launchconfiguration.system import EPUSystemWithLocalLaunchConfiguration
from pyhantom.system.tester import TestSystem

class PhantomConfig(object):
    def __init__(self, CFG):
        self._CFG = CFG
        self._logger = logging.getLogger("phantom")

        if self._CFG.phantom.authz.type == "simple_file":
            fname = self._CFG.phantom.authz.filename
            self._authz = SimpleFileDataStore(fname)
        elif self._CFG.phantom.authz.type == "cumulus":
            dburl = self._CFG.phantom.authz.dburl
            self._authz = CumulusDataStore(dburl)
        else:
            raise PhantomAWSException('InternalFailure', details="Phantom authz module is not setup.")

        if self._CFG.phantom.system.type == "tester":
            self._system = TestSystem()
        elif self._CFG.phantom.system.type == "local_launch_config_epu":
            self._system = EPUSystemWithLocalLaunchConfiguration(self._CFG, log=self._logger)
        else:
            raise PhantomAWSException('InternalFailure', details="Phantom authz module is not setup.")

    def get_system(self):
        return self._system

    def get_logger(self):
        return self._logger

    def get_authz(self):
        return self._authz


def determine_path():
    """find path of current file,
    Borrowed from wxglade.py"""
    root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    return os.path.dirname(os.path.abspath(root))

def validate_config(CFG):
    try:
        x = CFG.phantom.system
        x = CFG.phantom.authz
    except AttributeError, ex:
        raise PhantomAWSException('InternalFailure', details="Phantom is not properly configured. %s" % (str(ex)))

def build_cfg():
    config_files = []
    default_c = os.path.join(determine_path(), "config", "default.yml")
    root_c = "/etc/phantom/config.yml"
    user_c = os.path.expanduser("~/.phantom/config.yml")
    candidate_files = [default_c, root_c, user_c]
    env_str = 'PHANTOM_CONFIG'
    if env_str in os.environ:
        candidate_files.append(os.environ[env_str])

    for c in candidate_files:
        if os.path.exists(c):
            config_files.append(c)

    CFG = dashi.bootstrap.configure(config_files=config_files)
    validate_config(CFG)
    return PhantomConfig(CFG)