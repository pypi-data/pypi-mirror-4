"""
SNDFILE.IO

A simple module providing a unified API to read and write sound-files to and from
numpy arrays. If no extra modules are installed, it uses the standard library
to read and write uncompressed formats (WAV, AIFF)

If other modules are installed (scikits.audiolab, for example), it uses that
and more formats are supported

API
===

read_sndfile(path) 
    it will read ALL the samples and return a Sample --a tuplet (data, samplerate)
    Data will always be as a numpy.float64, between -1 and 1,
    independently of bit-rate

get_info(path)
    return SndInfo, a namedtuple with all the information of the 
    sound-file

write_sndfile(samples, samplerate, outfile, encoding='auto')
    write the samples. samples need to be a numpy.float64 array with 
    data between -1 and 1

"""
from .sndfileio import *
from .sndfileio import _compare_read