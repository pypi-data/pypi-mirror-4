from path import path
from proxy import Proxy
from pysimavr.logger import init_simavr_logger
from swig.simavr import elf_firmware_t, elf_read_firmware


class Firmware(Proxy):
    _reserved = 'mcu filename read'.split()

    def __init__(self, filename=None):
        init_simavr_logger()
        self.filename = None
        self.backend = elf_firmware_t()
        if filename:
            self.read(filename)

    def read(self, filename):
        filename = path(filename).abspath()
        ret = elf_read_firmware(str(filename), self.backend)
        if ret == -1:
            raise ValueError(filename + ' could not be loaded!')
        self.filename = filename

    @property
    def mcu(self):
        return self.mmcu

    @mcu.setter
    def mcu(self, value):
        self.mmcu = value
