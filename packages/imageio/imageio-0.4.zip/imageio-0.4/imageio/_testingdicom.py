
import os
import sys
import time
import struct
import numpy
import numpy as np

# From six.py
PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,    
    text_type = str
    binary_type = bytes
else:
    string_types = basestring,
    text_type = unicode
    binary_type = str

# Determine endianity of system
sys_is_little_endian = (sys.byteorder == 'little')

# Define a dictionary that contains the tags that we would like to know
MINIDICT =  {   (0x7FE0, 0x0010): ('PixelData',             'OB'),
                # Date and time
                (0x0008, 0x0020): ('StudyDate',             'DA'),
                (0x0008, 0x0021): ('SeriesDate',            'DA'),
                (0x0008, 0x0022): ('AcquisitionDate',       'DA'),
                (0x0008, 0x0023): ('ContentDate',           'DA'),
                (0x0008, 0x0030): ('StudyTime',             'TM'),
                (0x0008, 0x0031): ('SeriesTime',            'TM'),
                (0x0008, 0x0032): ('AcquisitionTime',       'TM'),
                (0x0008, 0x0033): ('ContentTime',           'TM'),
                # With what, where, by whom?
                (0x0008, 0x0060): ('Modality',              'CS'),
                (0x0008, 0x0070): ('Manufacturer',          'LO'),
                (0x0008, 0x0080): ('InstitutionName',       'LO'),
                # Descriptions 
                (0x0008, 0x1030): ('StudyDescription',      'LO'),
                (0x0008, 0x103E): ('SeriesDescription',     'LO'),
                # UID's                
                (0x0020, 0x0016): ('SOPClassUID',           'UI'),
                (0x0020, 0x0018): ('SOPInstanceUID',        'UI'),
                (0x0020, 0x000D): ('StudyInstanceUID',      'UI'),
                (0x0020, 0x000E): ('SeriesInstanceUID',     'UI'),
                (0x0008, 0x0117): ('ContextUID',            'UI'),
                # Numbers
                (0x0020, 0x0011): ('SeriesNumber',          'IS'),
                (0x0020, 0x0012): ('AcquisitionNumber',     'IS'),
                (0x0020, 0x0013): ('InstanceNumber',        'IS'),
                (0x0020, 0x0014): ('IsotopeNumber',         'IS'),
                (0x0020, 0x0015): ('PhaseNumber',           'IS'),
                (0x0020, 0x0016): ('IntervalNumber',        'IS'),
                (0x0020, 0x0017): ('TimeSlotNumber',        'IS'),
                (0x0020, 0x0018): ('AngleNumber',           'IS'),
                (0x0020, 0x0019): ('ItemNumber',            'IS'),
                (0x0020, 0x0020): ('PatientOrientation',    'CS'),
                (0x0020, 0x0030): ('ImagePosition',         'CS'),
                (0x0020, 0x0032): ('ImagePositionPatient',  'CS'),
                (0x0020, 0x0035): ('ImageOrientation',      'CS'),
                (0x0020, 0x0037): ('ImageOrientationPatient', 'CS'),
                
                # Patient infotmation
                (0x0010, 0x0010): ('PatientName',           'PN'),
                (0x0010, 0x0020): ('PatientID',             'LO'),
                (0x0010, 0x0030): ('PatientBirthDate',      'DA'),
                (0x0010, 0x0040): ('PatientSex',            'CS'),
                (0x0010, 0x1010): ('PatientAge',            'AS'),
                (0x0010, 0x1020): ('PatientSize',           'DS'),
                (0x0010, 0x1030): ('PatientWeight',         'DS'),
                
                # Image specific (required to construct numpy array)
                (0x0028, 0x0002): ('SamplesPerPixel',       'US'),
                (0x0028, 0x0008): ('NumberOfFrames',        'IS'),
                (0x0028, 0x0100): ('BitsAllocated',         'US'),
                (0x0028, 0x0101): ('BitsStored',            'US'),
                (0x0028, 0x0102): ('HighBit',               'US'),
                (0x0028, 0x0103): ('PixelRepresentation',   'US'),
                (0x0028, 0x0010): ('Rows',                  'US'),
                (0x0028, 0x0011): ('Columns',               'US'),
                (0x0028, 0x0052): ('RescaleIntercept',      'DS'),
                (0x0028, 0x0053): ('RescaleSlope',          'DS'),
            }

# Define set of groups that we're interested in (so we can quickly skip others)
GROUPS = set([key[0] for key in MINIDICT.keys()])
VRS = set([val[1] for val in MINIDICT.values()])

# todo: what about rescale slope and rescale intercept

class SimpleDicomReader(object):
    """ SimpleDicomReader
    
    This class provides reading of pixel data from DICOM files. It is 
    focussed on getting the pixel data, not the meta info.
    
    Usage: SimpleDicomReader.read(file_or_filename) -> info_dict
    
    Comparison with Pydicom
    -----------------------
    
    This code focusses on getting the pixel data out, which allows some
    shortcuts, resulting in the code being much smaller.
    
    Since the processing of data elements is much cheaper (it skips a lot
    of tags), this code is about 3x faster than pydicom (except for the
    deflated DICOM files).
    
    This class does borrow some code (and ideas) from the pydicom
    project, and (to the best of our knowledge) has the same limitations
    as pydicom with regard to the type of files that it can handle.
    
    Limitations
    -----------

    For more advanced DICOM processing, please check out pydicom.
    
      * Only a predefined subset of data elements (meta information) is read.
      * This is a reader; it can not write DICOM files.
      * (just like pydicom) it can handle none of the compressed DICOM
        formats except for "Deflated Explicit VR Little Endian"
        (1.2.840.10008.1.2.1.99). 
        
    """ 
    
    @classmethod
    def read(cls, file):
        """ read(file_or_filename)
        Get info_dict for the given file. info_dict['pixel_array'] is the
        numpy array.
        """ 
        reader = cls(file)    
        reader._read()
        return reader._info
    
    def __init__(self, file):
        # Open file if filename given
        if isinstance(file, string_types):
            file = open(file, 'rb')
        self._file = file
        # The meta header is always explicit and little endian
        self.is_implicit_VR = False
        self.is_little_endian = True
        self._unpackPrefix = '<'
        # Dict to store data elements of interest in
        self._info = {}
        # VR Conversion
        self._converters = {
                # Numbers
                'US': lambda x: self._unpack('H', x),
                'UL': lambda x: self._unpack('L', x),
                # Numbers encoded as strings
                'DS': lambda x: float( x.decode('ascii').strip('\x00') ),
                'IS': lambda x: int( x.decode('ascii').strip('\x00') ),
                # strings
                'AS': lambda x: x.decode('ascii').strip('\x00'),
                'DA': lambda x: x.decode('ascii').strip('\x00'),                
                'TM': lambda x: x.decode('ascii').strip('\x00'),
                'UI': lambda x: x.decode('ascii').strip('\x00'),
                'LO': lambda x: x.decode('utf-8').strip('\x00').rstrip(),
                'CS': lambda x: x.decode('ascii').strip('\x00').strip(),
                'PN': lambda x: x.decode('utf-8').strip('\x00').rstrip(),
            }
    
    def _unpack(self, fmt, value):
        return struct.unpack(self._unpackPrefix+fmt, value)[0]
    
    # Really only so we need minimal changes to _pixel_data_numpy
    def __iter__(self):
        return iter(self._info.keys())
    def __getattr__(self, key):
        info = object.__getattribute__(self, '_info')
        if key in info:
            return info[key]
        return object.__getattribute__(self, key)
    
    def _read(self):
        f = self._file
        # Check prefix after peamble
        f.seek(128)
        if f.read(4) != b'DICM':
            raise ValueError('Not a valid DICOM file.')
        # Read
        self._read_header()
        self._read_data_elements()
        # Get image, set pixel data to None to preserve memory
        self._info['pixel_array'] = self._pixel_data_numpy()
        self._info['PixelData'] = None
    
    def _readDataElement(self):
        f = self._file
        # Get group  and element
        group = self._unpack('H', f.read(2))
        element = self._unpack('H', f.read(2))
        # Get value length
        if self.is_implicit_VR:
            vl = self._unpack('I', f.read(4))
        else:
            vr = f.read(2)
            if vr in (b'OB', b'OW', b'SQ', b'UN'):
                reserved = f.read(2)
                vl = self._unpack('I', f.read(4))
            else:
                vl = self._unpack('H', f.read(2))
        # Get value
        value = f.read(vl)
        return group, element, value
    
    def _read_header(self):
        f = self._file
        TransferSyntaxUID = None
        
        # Read all elements, store transferSyntax when we encounter it
        try:
            while True:
                fp_save = f.tell()
                # Get element
                group, element, value = self._readDataElement()
                if group==0x02:
                    if group==0x02 and element==0x10:
                        TransferSyntaxUID = value.decode('ascii').strip('\x00') 
                else:
                    # No more group 2: rewind and break (don't trust group length)
                    f.seek(fp_save)
                    break
        except (EOFError, struct.error):
            raise RuntimeError('End of file reached while still reading header.')
        
        # Handle transfer syntax
        self._info['TransferSyntaxUID'] = TransferSyntaxUID
        #
        if TransferSyntaxUID is None: # Assume ExplicitVRLittleEndian
            is_implicit_VR, is_little_endian = False, True
        elif TransferSyntaxUID == '1.2.840.10008.1.2.1': # ExplicitVRLittleEndian
            is_implicit_VR, is_little_endian = False, True
        elif TransferSyntaxUID == '1.2.840.10008.1.2.2':  # ExplicitVRBigEndian
            is_implicit_VR, is_little_endian = False, False
        elif TransferSyntaxUID == '1.2.840.10008.1.2': # implicit VR little endian
            is_implicit_VR, is_little_endian = True, True
        elif TransferSyntaxUID == '1.2.840.10008.1.2.1.99':  # DeflatedExplicitVRLittleEndian:
            is_implicit_VR, is_little_endian = False, True
            self._inflate()
        elif TransferSyntaxUID == '1.2.840.10008.1.2.4.70': 
            is_implicit_VR, is_little_endian = False, True
        else:
            raise RuntimeError('The simple dicom reader can only read files ' +
                        'with uncompressed image data (not %r)' % TransferSyntaxUID)
                        
        # From hereon, use implicit/explicit big/little endian
        self.is_implicit_VR = is_implicit_VR
        self.is_little_endian = is_little_endian
        self._unpackPrefix = '><'[is_little_endian]
    
    def _read_data_elements(self):
        info = self._info
        try:  
            while True:
                # Get element
                group, element, value = self._readDataElement()
                # Is it a group we are interested in?
                if group in GROUPS:
                    key = (group, element)                    
                    name, vr = MINIDICT.get(key, (None, None))
                    # Is it an element we are interested in?
                    if name:
                        # Store value
                        converter = self._converters.get(vr, lambda x:x)
                        info[name] = converter(value)
        except (EOFError, struct.error):
            pass # end of file ...
    
    def _pixel_data_numpy(self):
        """Return a NumPy array of the pixel data.
        """
        # Taken from pydicom
        # Copyright (c) 2008-2012 Darcy Mason
        
        if not 'PixelData' in self:
            raise TypeError("No pixel data found in this dataset.")
        
        # determine the type used for the array
        need_byteswap = (self.is_little_endian != sys_is_little_endian)
        
        # Make NumPy format code, e.g. "uint16", "int32" etc
        # from two pieces of info:
        #    self.PixelRepresentation -- 0 for unsigned, 1 for signed;
        #    self.BitsAllocated -- 8, 16, or 32
        format_str = '%sint%d' % (('u', '')[self.PixelRepresentation],
                                  self.BitsAllocated)
        try:
            numpy_format = numpy.dtype(format_str)
        except TypeError:
            raise TypeError("Data type not understood by NumPy: "
                            "format='%s', PixelRepresentation=%d, BitsAllocated=%d" % (
                            numpy_format, self.PixelRepresentation, self.BitsAllocated))

        # Have correct Numpy format, so create the NumPy array
        arr = numpy.fromstring(self.PixelData, numpy_format)

        # XXX byte swap - may later handle this in read_file!!?
        if need_byteswap:
            arr.byteswap(True)  # True means swap in-place, don't make a new copy
        # Note the following reshape operations return a new *view* onto arr, but don't copy the data
        if 'NumberOfFrames' in self and self.NumberOfFrames > 1:
            if self.SamplesPerPixel > 1:
                arr = arr.reshape(self.SamplesPerPixel, self.NumberOfFrames, self.Rows, self.Columns)
            else:
                arr = arr.reshape(self.NumberOfFrames, self.Rows, self.Columns)
        else:
            if self.SamplesPerPixel > 1:
                if self.BitsAllocated == 8:
                    arr = arr.reshape(self.SamplesPerPixel, self.Rows, self.Columns)
                else:
                    raise NotImplementedError("This code only handles SamplesPerPixel > 1 if Bits Allocated = 8")
            else:
                arr = arr.reshape(self.Rows, self.Columns)
        return arr
    
    def _inflate(self):
        # Taken from pydicom
        # Copyright (c) 2008-2012 Darcy Mason
        import zlib
        from io import BytesIO
        # See PS3.6-2008 A.5 (p 71) -- when written, the entire dataset
        #   following the file metadata was prepared the normal way,
        #   then "deflate" compression applied.
        #  All that is needed here is to decompress and then
        #      use as normal in a file-like object
        zipped = self._file.read()
        # -MAX_WBITS part is from comp.lang.python answer:
        # groups.google.com/group/comp.lang.python/msg/e95b3b38a71e6799
        unzipped = zlib.decompress(zipped, -zlib.MAX_WBITS)
        self._file = BytesIO(unzipped)  # a file-like object


if __name__ == '__main__':
    N = 10
    import visvis as vv
    vv.closeAll()
    
    for variant in ['little', 'big', 'implicit', 'deflated']:
        filename = '/home/almar/data/dicom/test/test01_%s.DCM' % variant
        time0 = time.time()
        for i in range(N):
            im1,info1 = SimpleDicomReader.read(filename)
        print('simple reader took %1.3f s' % (time.time()-time0))
        vv.figure(); vv.clf()
        vv.subplot(121)
        t1 = vv.imshow(im1)
        
        import dicom
        time0 = time.time()
        for i in range(N):
            d = dicom.read_file(filename)
            im2 = d.pixel_array
        print('pydicom reader took %1.3f s' % (time.time()-time0))
        vv.subplot(122)
        t2 = vv.imshow(im2)
    
    
    
    