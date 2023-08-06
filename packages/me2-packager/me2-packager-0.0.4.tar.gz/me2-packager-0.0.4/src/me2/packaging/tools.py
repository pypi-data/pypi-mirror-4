'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''


import zipfile
import zlib
import io


class ZipFileByteIO(io.IOBase):
    """Class providing filelike access to zipped file
    
    fobj is expected to be at position 0
    
    ToDo: Check why it does not work with tarfile.extractfile but it work with extractall
    
    """
    def __init__(self, fobj, arcname):
        self.arcname = arcname
        self._raw_position = 0
        self._current_buffer = ""
        self._read_block_size = 16384
        self._zip_read_buffer = bytearray()

        self._zip = zipfile.ZipFile(fobj, "r")
        self._zinfo = self._zip.getinfo(arcname)
        self._fsize = self._zinfo.file_size

        self._src = fobj
        self._src.seek(self._zinfo.header_offset)
        self._src.read(30)
        self._src.read(len(self._zinfo.filename)) # Skip the file name
        if len(self._zinfo.extra) > 0: self._src.read(len(self._zinfo.extra))
        if len(self._zinfo.comment) > 0: self._src.read(len(self._zinfo.comment))
        self._decomp = zlib.decompressobj(-15) # ToDO: A bit of misery this -15

    def readable(self):
        return True

    def seekable(self):
        return False

    def readinto(self, buf):
        # Check that we have enough data
        start_output_block = 0
        available_data_length = len(self._zip_read_buffer)
        buf_size = len(buf)
        if available_data_length >= buf_size:
            buf[start_output_block:] = self._zip_read_buffer[0:buf_size]
            self._zip_read_buffer = self._zip_read_buffer[buf_size:]
            return buf_size # We can return directly
        else:
            buf[start_output_block:available_data_length] = self._zip_read_buffer
            self._zip_read_buffer = bytearray()
        start_output_block = available_data_length

        if self._raw_position >= self._zinfo.compress_size: # Consumed the entire compressed input
            temp = self._decomp.flush()
        else:
            if (self._raw_position + self._read_block_size) > self._zinfo.compress_size:
                bsize = self._zinfo.compress_size - self._raw_position # -1
            else:
                bsize = self._read_block_size
            temp = self._decomp.decompress(self._src.read(bsize))
            self._raw_position += bsize

        read_size = len(temp)

        usable_size = read_size
        if (read_size + start_output_block) > buf_size: # Got more data then we need
            usable_size = buf_size - start_output_block

        buf[start_output_block:start_output_block + usable_size] = temp[0:usable_size]
        self._zip_read_buffer = temp[usable_size:]
        return start_output_block + usable_size


    def close(self):
        io.IOBase.close(self)
        self._src.close()

def zip_file_buffer(file_object, zipped_file):
    """Return a file like object for a file inside a zip file
    
    ToDo: Check why it does not work with tarfile.extractfile but it work with extractall
    """
    return io.BufferedReader(ZipFileByteIO(file_object, zipped_file))


def sha1_fileobj(f):
    """Computes sha1 hash from file like object
    It expects that the file like object is at position 0
    """
    import hashlib
    m = hashlib.sha1()
    while True:
        buf = f.read(1024)
        if len(buf) <= 0:
            break
        m.update(buf)

    return m.hexdigest()


