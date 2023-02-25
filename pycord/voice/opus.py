# cython: language_level=3
# Copyright (c) 2021-present Pycord Development
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

import array
import ctypes
import ctypes.util
import os
import struct
import sys
from typing import Any

from ..enums import Enum
from ..errors import PycordException


class OpusException(PycordException):
    """Raises when an exception related to Opus occurs"""


c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)


class BandwidthControl(Enum):
    narrow = 1101
    medium = 1102
    wide = 1103
    superwide = 1104
    full = 1105


class SignalControl(Enum):
    auto = -1000
    voice = 3001
    music = 3002


class EncoderStruct(ctypes.Structure):
    pass


class DecoderStruct(ctypes.Structure):
    pass


EncoderStructPtr = ctypes.POINTER(EncoderStruct)
DecoderStructPtr = ctypes.POINTER(DecoderStruct)


class BaseOpus:
    _GENEXPORT = {
        'opus_get_version_string': ([[], ctypes.c_char_p, None]),
        'opus_strerror': ([[ctypes.c_int], ctypes.c_char_p, None]),
    }
    _EXPORT = {}

    def __init__(self, library_path: str | None = None) -> None:
        self._path = library_path or self._get_path()

        if self._path is None:
            raise ('Path for opus library not found')

        self.dll = ctypes.cdll.LoadLibrary(self._path)

        export = {}
        export.update(self._GENEXPORT)
        export.update(self._EXPORT)

        for name, bind in export:
            func = getattr(self.dll, name)

            if bind[0]:
                func.argtypes = bind[0]

            func.restype = bind[1]

            setattr(self, name, func)

    def _get_path(self) -> str | None:
        try:
            if sys.platform == 'win32':
                _basedir = os.path.dirname(os.path.abspath(__file__))
                _bitness = struct.calcsize('P') * 8
                _target = 'x64' if _bitness > 32 else 'x86'
                return os.path.join(_basedir, 'bin', f'libopus-0.{_target}.dll')
            else:
                return ctypes.util.find_library('opus')
        except Exception:
            return None


class Application(Enum):
    AUDIO = 2049
    VOIP = 2048
    LOWDELAY = 2051


class Control(Enum):
    SET_BITRATE = 4002
    SET_BANDWIDTH = 4008
    SET_FEC = 4012
    SET_PLP = 4014


class OpusEncoder(BaseOpus):
    _EXPORT = {
        'opus_encoder_get_size': ([ctypes.c_int], ctypes.c_int),
        'opus_encoder_create': (
            [ctypes.c_int, ctypes.c_int, ctypes.c_int, c_int_ptr],
            EncoderStructPtr,
        ),
        'opus_encode': (
            [
                EncoderStructPtr,
                c_int16_ptr,
                ctypes.c_int,
                ctypes.c_char_p,
                ctypes.c_int32,
            ],
            ctypes.c_int32,
        ),
        'opus_encoder_ctl': (None, ctypes.c_int32),
        'opus_encoder_destroy': ([EncoderStructPtr], None),
    }

    def __init__(self, application: Application = Application.AUDIO, library_path: str | None = None, sample_rate: int | None = None, frame_length: int | None = None):
        super(OpusEncoder, self).__init__(library_path)
        self.application = application

        self._encoder = None
        self.sample_rate = sample_rate or 48000
        self.frame_length: int = frame_length or 20

    @property
    def frame_size(self) -> int:
        return int(self.sample_rate / 1000 * self.frame_length)

    def initialize(self) -> None:
        self.create()
        self.set_bitrate(128)
        self.set_fec(True)
        self.set_expected_packet_loss_percent(0.15)
        self.set_bandwidth('full')
        self.set_signal_type('auto')

    def set_bitrate(self, kbps: int) -> None:
        self._check_created()

        kbps = min(128, max(16, int(kbps)))
        ret = self.opus_encoder_ctl(
            self._encoder, int(Control.SET_BITRATE.value), kbps * 1024
        )

        if ret < 0:
            raise OpusException('failed to set bitrate to {}: {}'.format(kbps, ret))

    def set_fec(self, value: bool) -> None:
        self._check_created()

        ret = self.opus_encoder_ctl(
            self._encoder, int(Control.SET_FEC.value), int(value)
        )

        if ret < 0:
            raise OpusException('failed to set FEC to {}: {}'.format(value, ret))

    def set_expected_packet_loss_percent(self, perc: int) -> None:
        self._check_created()

        ret = self.opus_encoder_ctl(
            self._encoder, int(Control.SET_PLP.value), min(100, max(0, int(perc * 100)))
        )

        if ret < 0:
            raise OpusException('failed to set PLP to {}: {}'.format(perc, ret))

    def set_bandwidth(self, band: BandwidthControl) -> None:
        self._check_created()
        if band not in BandwidthControl:
            raise KeyError(f'{band!r} is not a valid bandwidth setting')

        k = band.value
        self.opus_encoder_ctl(self._encoder, Control.SET_BANDWIDTH.value, k)

    def set_signal_type(self, sig: SignalControl) -> None:
        self._check_created()
        if sig not in SignalControl:
            raise KeyError(f'{sig!r} is not a valid signal setting')

        k = sig.value
        self.opus_encoder_ctl(self._encoder, Control.SET_SIGNAL.value, k)

    def _check_created(self) -> None:
        if self._encoder is None:
            raise OpusException('encoder has not been created yet')

    def create(self) -> None:
        ret = ctypes.c_int()
        result = self.opus_encoder_create(
            self.sampling_rate, self.channels, self.application.value, ctypes.byref(ret)
        )

        if ret.value != 0:
            raise OpusException('failed to create opus encoder: {}'.format(ret.value))

        self._encoder = result

    def destroy(self) -> None:
        self.opus_encoder_destroy(self._encoder)

    def encode(self, pcm: bytes) -> bytes:
        max_data_bytes = len(pcm)
        pcm = ctypes.cast(pcm, c_int16_ptr)
        data = (ctypes.c_char * max_data_bytes)()

        ret = self.opus_encode(self._encoder, pcm, self.frame_size, data, max_data_bytes)
        if ret < 0:
            raise OpusException(f'failed to encode: {ret}')

        return array.array('b', data[:ret]).tobytes()

    
# Subclass of OpusEncoder and OpusDecoder
class Opus(OpusEncoder):
    ...
