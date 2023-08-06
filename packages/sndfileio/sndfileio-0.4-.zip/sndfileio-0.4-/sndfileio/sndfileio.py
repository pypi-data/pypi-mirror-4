"""
SNDFILE.IO

A simple module providing a unified API to read and write sound-files to and from
numpy arrays. If no extra modules are installed, it uses only standard modules
and numpy to read and write uncompressed formats (WAV, AIFF).

If other modules are installed (scikits.audiolab, for example), it uses that
and more formats are supported.

Advantages over the built-in modules wave and aifc

* support for PCM16, PCM24, PCM32 and FLOAT32
* unified output format, independent of encoding --> always float64
* unified API for all backends

API
===

read_sndfile(path) --> it will read ALL the samples and return a Sample --a tuplet (data, samplerate)
                     | Data will always be as a numpy.float64, between -1 and 1,
                     | independently of bit-rate

get_info(path)     --> return SndInfo, a namedtuple with all the information of the sound-file

write_sndfile(samples, samplerate, outfile, encoding='auto')
                   --> write the samples. samples need to be a numpy.float64 array with data between -1 and 1

"""

from __future__ import division
import os
from collections import namedtuple
import numpy as np
import struct
import warnings

__all__ = [
    "read_sndfile",
    "read_sndfile_chunked",
    "get_info",
    "write_sndfile",
    "WavReader",
    "bitdepth",
    "mono"
]

Sample = namedtuple("Sample", "samples sr")
SndInfo = namedtuple("SndInfo", "samplerate nframes channels encoding fileformat")

class SndfileError(IOError):
    pass

def chunks(start, end, step):
    pos = start
    last_full = end - step
    while pos < last_full:
        yield pos, step
        pos += step
    yield pos, end - pos

class _Audiolab:
    priority = 1
    supported_filetypes =  [".aif", ".aiff", ".wav", ".flac", ".ogg", ".wav64", ".caf", ".raw"]
    can_read_in_chunks = True
    @staticmethod
    def is_available():
        try:
            import scikits.audiolab; return True
        except ImportError:
            return False
    @staticmethod
    def read(path):
        from scikits import audiolab
        snd = audiolab.Sndfile(path)
        data = snd.read_frames(snd.nframes)
        sr = snd.samplerate
        return Sample(data, sr)
    @staticmethod
    def read_chunked(path, frames=100):
        from scikits import audiolab
        snd = audiolab.Sndfile(path)
        if with_position:
            for pos, nframes in chunks(0, snd.nframes, frames):
                yield snd.read_frames(nframes), pos
        else:
            for pos, nframes in chunks(snd.nframes):
                yield snd.read_frames(nframes)
    @staticmethod
    def get_info(path):
        from scikits import audiolab
        snd = audiolab.Sndfile(path)
        return SndInfo(snd.samplerate, snd.nframes, snd.channels, snd.encoding, snd.file_format)

class _Builtin:
    priority = 100
    supported_filetypes = [".wav", ".aif", ".aiff"] # aif not working!!!
    can_read_in_chunks = False
    @staticmethod
    def is_available(): return True
    @staticmethod
    def read(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in (".aif", ".aiff"):
            return AiffReader(path).read()
        elif ext == ".wav":
            return WavReader(path).read()
        else:
            raise ValueError("format not supported")
    @staticmethod
    def get_info(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in (".aif", ".aiff"):
            return AiffReader(path).info
            # return _aiff_get_info(path)
        elif ext == ".wav":
            return WavReader(path).info
    @staticmethod
    def read_chunked(path, frames=100):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.wav':
            return WavReader(path).read_chunked(path, frames)
        else:
            raise NotImplementedError

class _SndfileReader(object):
    @property
    def info(self):
        if self._info is not None:
            return self._info
        self._info = self._get_info()
        return self._info   
    def read(self):
        pass
    def read_chunked(self):
        raise NotImplementedError

class WavReader(_SndfileReader):
    def __init__(self, path):
        self.path = path
        fsize, self._big_endian = _wav_read_riff_chunk(open(path))
        self._info = None
    def _get_info(self):
        return _wav_get_info(self.path)
    def read(self):
        sample, info = _wav_read(self.path)
        self._info = info
        return sample
    def read_chunked(self, frames=100):
        return _wav_read_chunked(self.path, frames)

class AiffReader(_SndfileReader):
    def __init__(self, path):
        self.path = path
        self._info = None
    def _get_info(self):
        return _aiff_get_info(self.path)
    def read(self):
        sample, info = _aiff_read(self.path)
        self._info = info
        return sample
    
def _aiff_get_info(path):
    import aifc
    f = aifc.open(path)
    bytes = f.getsampwidth()
    if bytes == 4:
        raise IOError("32 bit aiff is not supported yet!")
    encoding = "pcm%d" % (bytes * 8)
    return SndInfo(f.getframerate(), f.getnframes(), f.getnchannels(), encoding, "aiff")

def _aiff_read(path):
    import aifc
    f = aifc.open(path)
    datastr = f.readframes(f.getnframes())
    bytes = f.getsampwidth()
    channels = f.getnchannels()
    encoding = "pcm%d" % (bytes * 8)
    if encoding == 'pcm8':
        data = (np.fromstring(datastr, dtype=np.int8) / (2.0**7)).astype(float)
    elif encoding == 'pcm16':
        data = (np.fromstring(datastr, dtype=">i2") / (2.0**15)).astype(float)
    elif encoding == 'pcm24':
        data = np.fromstring(datastr, dtype=np.ubyte)
        data = _numpy_24bit_to_32bit(data, bigendian=True).astype(float) / (2.0**31)
    elif encoding == 'pcm32':
        data = (np.fromstring(datastr, dtype=">i4") / (2.0**31)).astype(float)
    if channels > 1:
        data = data.reshape(-1, channels)
    info = SndInfo(f.getframerate(), f.getnframes(), f.getnchannels(), encoding, "aiff")
    return Sample(data, info.samplerate), info

def _floatize(data, encoding):
    assert (data > 0).any()
    if encoding == 'flt32':
        return data
    elif encoding == 'pcm24':
        return data / (2.0 ** 31)
    elif encoding == 'pcm16':
        return data / (2.0 ** 15)
    else:
        raise ValueError("encoding not understood")

def _encoding(format, bits):
    """
    format, bits as returned by _wav_read_fmt_chunk

    format: "pcm", "float"
    bits  : 16, 24, 32
    """
    return "%s%d" % (format, bits)
        
def _wav_read_riff_chunk(fid):
    big_endian = False
    asbytes = str
    str1 = fid.read(4)
    if str1 == asbytes('RIFX'):
        big_endian = True
    elif str1 != asbytes('RIFF'):
        raise ValueError("Not a WAV file.")
    if big_endian:
        fmt = '>I'
    else:
        fmt = '<I'
    fsize = struct.unpack(fmt, fid.read(4))[0] + 8
    str2 = fid.read(4)
    if (str2 != asbytes('WAVE')):
        raise ValueError("Not a WAV file.")
    if str1 == asbytes('RIFX'):
        big_endian = True
    return fsize, big_endian

def _wav_read_fmt_chunk(f, big_endian):
    fmt = ">" if big_endian else "<"
    res = struct.unpack(fmt + 'ihHIIHH', f.read(20))
    chunksize, format, ch, sr, brate, ba, bits = res
    formatstr = {
         1:'pcm',
         3:'flt',
         6:'alw',  # alaw
         7:'mlw'   # mulaw
        -2:'ext'   # extensible
    }.get(format)
    if formatstr is None:
        raise SndfileError("could not understand format while reading wav file")
    if formatstr == 'ext':
        raise SndfileError("extension formats are not supported yet")
    if chunksize > 16:
        f.read(chunksize - 16)
    return chunksize, formatstr, ch, sr, brate, ba, bits

def _wav_read_data(fid, size, channels, encoding, big_endian):
    """
    adapted from scipy.io.wavfile._read_data_chunk

    assume we are at the data (after having read the size)
    """
    bits = int(encoding[3:])
    if bits == 8:
        data = np.fromfile(fid, dtype=np.ubyte, count=size)
        if channels > 1:
            data = data.reshape(-1, channels)
    else:
        bytes = bits//8
        if encoding in ('pcm16', 'pcm32', 'pcm64'):
            if big_endian:
                dtype = '>i%d' % bytes
            else:
                dtype = '<i%d' % bytes
            data = np.fromfile(fid, dtype=dtype, count=size//bytes)
            if channels > 1:
                data = data.reshape(-1, channels)
        elif encoding[:3] == 'flt':
            print "flt32!"
            if bits == 32:
                if big_endian:
                    dtype = '>f4'
                else:
                    dtype = '<f4'
            else:
                raise NotImplementedError
            data = np.fromfile(fid, dtype=dtype, count=size//bytes)
            if channels > 1:
                data = data.reshape(-1, channels)
        elif encoding == 'pcm24':
            # this conversion approach is really bad for long files
            # TODO: do the same but in chunks
            data = _numpy_24bit_to_32bit(np.fromfile(fid, dtype=np.ubyte, count=size), bigendian=False)
            if channels > 1:
                data = data.reshape(-1, channels)
    return data

def _numpy_24bit_to_32bit(data, bigendian=False):
    """
    data is a ubyte array of shape = (size,) (interleaved channels if multichannel)
    """
    target = np.zeros((data.shape[0]*4/3,), dtype=np.ubyte)
    if not bigendian:
        target[3::4] = data[2::3]
        target[2::4] = data[1::3]
        target[1::4] = data[0::3]
    else:
        target[1::4] = data[2::3]
        target[2::4] = data[1::3]
        target[3::4] = data[0::3]
    del data
    targetraw = target.tostring()
    del target
    data = np.fromstring(targetraw, dtype=np.int32)
    return data

def _wav_read(path, convert_to_float=True):
    f = open(path, 'rb')
    info, fsize, big_endian, datasize = _wav_get_info(f, extended=True)
    asbytes = str
    fmt = ">i" if big_endian else "<i"
    bits = int(info.encoding[3:])
    data = _wav_read_data(f, datasize, info.channels, info.encoding, big_endian)
    f.close()
    if convert_to_float:
        data = _floatize(data, info.encoding).astype(float)
    return Sample(data, info.samplerate), info

def _wav_read_chunked(path, frames=100, convert_to_float=True):
    f = open(path, 'rb')
    info, fsize, big_endian, datasize = _wav_get_info(f, extended=True)
    if info.encoding == 'flt32':
        raise NotImplementedError("float-32 is not correctly implemented, aborting!")
    asbytes = str
    fmt = ">i" if big_endian else "<i"
    bits = int(info.encoding[3:])
    bytes = bits//8
    chunksize = bytes * info.channels * frames
    if bits == 8:
        raise NotImplementedError
    else:
        if big_endian:
            dtype = '>i%d' % bytes
        else:
            dtype = '<i%d' % bytes
        for _, chunk in chunks(0, chunksize, datasize):
            data = np.fromfile(f, dtype=dtype, count=chunk//bytes)
            if info.channels > 1:
                data = data.reshape(-1, info.channels)
            if convert_to_float:
                data = _floatize(data, info.encoding)
            yield data
    f.close()

def _wav_get_info(f, extended=False):
    """
    read the info of a wav file. taken mostly from scipy.io.wavfile

    if extended: returns also fsize and big_endian
    """
    if isinstance(f, basestring):
        f = open(f, 'rb')
        needsclosing = True
    else:
        needsclosing = False
    fsize, big_endian = _wav_read_riff_chunk(f)
    if big_endian:
        fmt = ">i"
    else:
        fmt = "<i"
    while (f.tell() < fsize):
        chunk_id = f.read(4)
        if chunk_id == 'fmt ':
            chunksize, sampleformat, channels, samplerate, byterate, block_align, bits = _wav_read_fmt_chunk(f, big_endian)
        elif chunk_id == 'data':
            datasize = struct.unpack(fmt, f.read(4))[0]
            # size = numsamples * NumChannels * BitsPerSample/8
            nframes = int(datasize / (channels * (bits/8)))
            break
        else:
            warnings.warn("chunk not understood: %s" % chunk_id)
            data = f.read(4)
            size = struct.unpack(fmt, data)[0]
            f.seek(size, 1)
    encoding = _encoding(sampleformat, bits)
    if needsclosing:
        f.close() 
    info = SndInfo(samplerate, nframes, channels, encoding, "wav")    
    if extended:
        return info, fsize, big_endian, datasize
    return info
  
def _get_backend(path=None, key=None):
    """
    ext: a string like .aiff. If given, only backends supporting the given filetype are returned
    """
    if path:
        ext = os.path.splitext(path)[1].lower()
    else:
        ext = None
    backends = [_Builtin, _Audiolab]
    backends = [b for b in backends if b.is_available()]
    if key:
        backends = [b for b in backends if key(b)]
    if ext:
        backends = [backend for backend in backends if ext in backend.supported_filetypes]
    if backends:
        best = sorted(backends, key=lambda backend: backend.priority)[0]
        return best
    return None
    
def read_sndfile(path):
    """
    read a soundfile as a numpy array. returns (data, sr)
    """
    backend = _get_backend(path)
    return backend.read(path)

def read_sndfile_chunked(path, frames=100):
    """
    returns a generator yielding numpy arrays (float64) of at most `frames` frames
    """
    backend = _get_backend(path, key=lambda backend: backend.can_read_in_chunks)
    if backend:
        return backend.read_chunked(path, frames)
    else:
        raise SndfileError("chunked reading is not supported. Try installing scikits.audiolab")

def get_info(path):
    backend = _get_backend(path)
    return backend.get_info(path)

def write_sndfile(samples, sr, outfile, encoding='auto'):
    """
    samples  --> array-like. the actual samples, shape=(nframes, channels)
    sr       --> sampling-rate
    outfile  --> the name of the outfile. the extension will determine the file-format
    encoding --> if other than 'auto', it determines de encoding of the file
                 | one of: 
                 |   - 'pcm16'
                 |   - 'pcm24'
                 |   - 'pcm32'
                 |   - 'flt32'

                 NB: not all file formats support all encodings. If the file-format does
                 not support the encoding, a SndfileError will the thrown

                 If set to 'auto', an encoding will be selected based on the file-format and
                 on the data. Basically, if your data is of integer type, a pcm encoding will
                 be chosen which is supported by the file-type. If data is of floating-type, 
                 a float32 encoding will be chosen if your file-type supports it. If not, the
                 best pcm encoding will be chosen
    """
    backend = _get_backend_for_write(path)
    if encoding == 'auto':
        encoding = _guess_encoding(data, outfile)
    data = _check_data_for_writing(data, encoding)
    return backend.write(data, sr, outfile, encoding)

def _get_write_backend(path, encoding):
    raise NotImplementedError("writing is still not implemented")

def mono(samples, mixdown=False):
    """
    return 
    """
    if len(samples.shape) == 1:
        return samples
    if not mixdown:
        return samples[:,0]
    else:
        raise NotImplementedError

def bitdepth(data, snap=True):
    """
    data: a numpy.array (mono or multi-channel)

    returns the number of bits actually used to represent the data
    snap: snap to 8, 16, 24 or 32 bits.
    """
    data = mono(data)
    maxitems = min(4096, data.shape[0])
    maxbits = max(x.as_integer_ratio()[1] for x in data[:maxitems]).bit_length()
    if snap:
        if maxbits <= 8:
            maxbits = 8
        elif maxbits <= 16:
            maxbits = 16
        elif maxbits <= 24:
            maxbits = 24
        elif maxbits <= 32:
            maxbits = 32
        elif maxbits <= 64:
            maxbits = 64
        else:
            raise ValueError("bitdepth too high!: %d" % maxbits)
    return maxbits
    
def _guess_encoding(data, outfile):
    ext = os.path.splitext(outfile)[1].lower()
    maxbits = bitdepth(data, snap=True)
    if ext in ('.wav .aif .aiff'.split()):
        encoding = {
            16: 'pcm16',
            24: 'pcm24',
            32: 'flt32'
        }.get(maxbits)
    elif ext == ".flac":
        encoding = {
            16: 'pcm16',
            24: 'pcm24',
            32: 'pcm24'
        }.get(maxbits)
    else:
        encoding = 'pcm24'
    return encoding

def _check_data_for_writing(data, encoding):
    pass

def _compare_read(path):
    s0 = _Audiolab.read(path)
    s1 = _Builtin.read(path)
    return s0, s1

def _testfile_builtin(path):
    s0, s1 = _compare_read(path)
    return (s0[0] == s1[0]).all()



