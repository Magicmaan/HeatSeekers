from os import getenv
from os import path
import platform
from dataclasses import dataclass, asdict
from program.identify_platform import PLATFORM, getPlatform
from .platform_directories import DIRECTORIES as _DIRECTORIES

#TODO: distinguish between platforms for directories
DIRECTORIES = _DIRECTORIES
@dataclass
class FILES:
    HOST: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "host.txt")
    CERTIFICATE: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "certs", "certificate.pem.crt")
    PRIVATE_KEY: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "certs", "private.pem.key")
    ROOT_CA: str = path.join(DIRECTORIES.CONNECTION_DATA_PATH, "certs", "ROOTCA1.pem")
    TOPICS: str = path.join(DIRECTORIES.CLIENT_DATA_PATH, "topics.txt")
DATA_PATH = DIRECTORIES.DATA_PATH
CONNECTION_DATA_PATH = DIRECTORIES.CONNECTION_DATA_PATH

#from .Logger import Logger

from .setup_program import SetupProgram
from .program import Program


__all__ = [
    'Program',
    'DIRECTORIES',
    'FILES',
    'DATA_PATH',
    'CONNECTION_DATA_PATH'
]
