import struct
import io
import sys
import datetime
import re

try :
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    
REDIS_RDB_6BITLEN = 0
REDIS_RDB_14BITLEN = 1
REDIS_RDB_32BITLEN = 2
REDIS_RDB_ENCVAL = 3

REDIS_RDB_OPCODE_EXPIRETIME_MS = 252
REDIS_RDB_OPCODE_EXPIRETIME = 253
REDIS_RDB_OPCODE_SELECTDB = 254
REDIS_RDB_OPCODE_EOF = 255

REDIS_RDB_TYPE_STRING = 0
REDIS_RDB_TYPE_LIST = 1
REDIS_RDB_TYPE_SET = 2
REDIS_RDB_TYPE_ZSET = 3
REDIS_RDB_TYPE_HASH = 4
REDIS_RDB_TYPE_HASH_ZIPMAP = 9
REDIS_RDB_TYPE_LIST_ZIPLIST = 10
REDIS_RDB_TYPE_SET_INTSET = 11
REDIS_RDB_TYPE_ZSET_ZIPLIST = 12
REDIS_RDB_TYPE_HASH_ZIPLIST = 13

REDIS_RDB_ENC_INT8 = 0
REDIS_RDB_ENC_INT16 = 1
REDIS_RDB_ENC_INT32 = 2
REDIS_RDB_ENC_LZF = 3

DATA_TYPE_MAPPING = {
    0 : "string", 1 : "list", 2 : "set", 3 : "sortedset", 4 : "hash", 
    9 : "hash", 10 : "list", 11 : "set", 12 : "sortedset", 13 : "hash"}

class RdbSplitter :
    """
    Split a given RDB file into multiple RDB Files
    """
    def __init__(self) :
        pass

    def split(self, filename):
        """
        Parse a redis rdb dump file, and call methods in the 
        callback object during the parsing operation.
        """
        with open(filename, "rb") as f:
            self.verify_magic_string(f.read(5))
            self.verify_version(f.read(4))
            db_number = 0
            while True :
                self._expiry = None
                data_type = read_unsigned_char(f)
                
                if data_type == REDIS_RDB_OPCODE_EXPIRETIME_MS :
                    self._expiry = to_datetime(read_unsigned_long(f) * 1000)
                    data_type = read_unsigned_char(f)
                elif data_type == REDIS_RDB_OPCODE_EXPIRETIME :
                    self._expiry = to_datetime(read_unsigned_int(f) * 1000000)
                    data_type = read_unsigned_char(f)
                
                if data_type == REDIS_RDB_OPCODE_SELECTDB :
                    db_number = self.read_length(f)
                    continue
                
                if data_type == REDIS_RDB_OPCODE_EOF :
                    break

                if self.matches_filter(db_number) :
                    self._key = self.read_string(f)
                    if self.matches_filter(db_number, self._key, data_type):
                        self.read_object(f, data_type)
                    else:
                        self.skip_object(f, data_type)
                else :
                    self.skip_key_and_object(f, data_type)

    def read_length_with_encoding(self, f) :
        length = 0
        is_encoded = False
        bytes = []
        bytes.append(read_unsigned_char(f))
        enc_type = (bytes[0] & 0xC0) >> 6
        if enc_type == REDIS_RDB_ENCVAL :
            is_encoded = True
            length = bytes[0] & 0x3F
        elif enc_type == REDIS_RDB_6BITLEN :
            length = bytes[0] & 0x3F
        elif enc_type == REDIS_RDB_14BITLEN :
            bytes.append(read_unsigned_char(f))
            length = ((bytes[0]&0x3F)<<8)|bytes[1]
        else :
            length = ntohl(f)
        return (length, is_encoded)

    def read_length(self, f) :
        return self.read_length_with_encoding(f)[0]

    def read_string(self, f) :
        tup = self.read_length_with_encoding(f)
        length = tup[0]
        is_encoded = tup[1]
        val = None
        if is_encoded :
            if length == REDIS_RDB_ENC_INT8 :
                val = read_signed_char(f)
            elif length == REDIS_RDB_ENC_INT16 :
                val = read_signed_short(f)
            elif length == REDIS_RDB_ENC_INT32 :
                val = read_signed_int(f)
            elif length == REDIS_RDB_ENC_LZF :
                clen = self.read_length(f)
                l = self.read_length(f)
                val = self.lzf_decompress(f.read(clen), l)
        else :
            val = f.read(length)
        return val

    # Read an object for the stream
    # f is the redis file 
    # enc_type is the type of object
    def read_object(self, f, enc_type) :
        if enc_type == REDIS_RDB_TYPE_STRING :
            val = self.read_string(f)
            self._callback.set(self._key, val, self._expiry, info={'encoding':'string'})
        elif enc_type == REDIS_RDB_TYPE_LIST :
            # A redis list is just a sequence of strings
            # We successively read strings from the stream and create a list from it
            # The lists are in order i.e. the first string is the head, 
            # and the last string is the tail of the list
            length = self.read_length(f)
            self._callback.start_list(self._key, length, self._expiry, info={'encoding':'linkedlist' })
            for count in xrange(0, length) :
                val = self.read_string(f)
                self._callback.rpush(self._key, val)
            self._callback.end_list(self._key)
        elif enc_type == REDIS_RDB_TYPE_SET :
            # A redis list is just a sequence of strings
            # We successively read strings from the stream and create a set from it
            # Note that the order of strings is non-deterministic
            length = self.read_length(f)
            self._callback.start_set(self._key, length, self._expiry, info={'encoding':'hashtable'})
            for count in xrange(0, length) :
                val = self.read_string(f)
                self._callback.sadd(self._key, val)
            self._callback.end_set(self._key)
        elif enc_type == REDIS_RDB_TYPE_ZSET :
            length = self.read_length(f)
            self._callback.start_sorted_set(self._key, length, self._expiry, info={'encoding':'skiplist'})
            for count in xrange(0, length) :
                val = self.read_string(f)
                dbl_length = read_unsigned_char(f)
                score = f.read(dbl_length)
                if isinstance(score, str):
                    score = float(score)
                self._callback.zadd(self._key, score, val)
            self._callback.end_sorted_set(self._key)
        elif enc_type == REDIS_RDB_TYPE_HASH :
            length = self.read_length(f)
            self._callback.start_hash(self._key, length, self._expiry, info={'encoding':'hashtable'})
            for count in xrange(0, length) :
                field = self.read_string(f)
                value = self.read_string(f)
                self._callback.hset(self._key, field, value)
            self._callback.end_hash(self._key)
        elif enc_type == REDIS_RDB_TYPE_HASH_ZIPMAP :
            self.read_zipmap(f)
        elif enc_type == REDIS_RDB_TYPE_LIST_ZIPLIST :
            self.read_ziplist(f)
        elif enc_type == REDIS_RDB_TYPE_SET_INTSET :
            self.read_intset(f)
        elif enc_type == REDIS_RDB_TYPE_ZSET_ZIPLIST :
            self.read_zset_from_ziplist(f)
        elif enc_type == REDIS_RDB_TYPE_HASH_ZIPLIST :
            self.read_hash_from_ziplist(f)
        else :
            raise Exception('read_object', 'Invalid object type %d for key %s' % (enc_type, self._key))

    def skip_key_and_object(self, f, data_type):
        self.skip_string(f)
        self.skip_object(f, data_type)

    def skip_string(self, f):
        tup = self.read_length_with_encoding(f)
        length = tup[0]
        is_encoded = tup[1]
        bytes_to_skip = 0
        if is_encoded :
            if length == REDIS_RDB_ENC_INT8 :
                bytes_to_skip = 1
            elif length == REDIS_RDB_ENC_INT16 :
                bytes_to_skip = 2
            elif length == REDIS_RDB_ENC_INT32 :
                bytes_to_skip = 4
            elif length == REDIS_RDB_ENC_LZF :
                clen = self.read_length(f)
                l = self.read_length(f)
                bytes_to_skip = clen
        else :
            bytes_to_skip = length
        
        skip(f, bytes_to_skip)

    def skip_object(self, f, enc_type):
        skip_strings = 0
        if enc_type == REDIS_RDB_TYPE_STRING :
            skip_strings = 1
        elif enc_type == REDIS_RDB_TYPE_LIST :
            skip_strings = self.read_length(f)
        elif enc_type == REDIS_RDB_TYPE_SET :
            skip_strings = self.read_length(f)
        elif enc_type == REDIS_RDB_TYPE_ZSET :
            skip_strings = self.read_length(f) * 2
        elif enc_type == REDIS_RDB_TYPE_HASH :
            skip_strings = self.read_length(f) * 2
        elif enc_type == REDIS_RDB_TYPE_HASH_ZIPMAP :
            skip_strings = 1
        elif enc_type == REDIS_RDB_TYPE_LIST_ZIPLIST :
            skip_strings = 1
        elif enc_type == REDIS_RDB_TYPE_SET_INTSET :
            skip_strings = 1
        elif enc_type == REDIS_RDB_TYPE_ZSET_ZIPLIST :
            skip_strings = 1
        elif enc_type == REDIS_RDB_TYPE_HASH_ZIPLIST :
            skip_strings = 1
        else :
            raise Exception('read_object', 'Invalid object type %d for key %s' % (enc_type, self._key))
        for x in xrange(0, skip_strings):
            self.skip_string(f)


    def read_intset(self, f) :
        raw_string = self.read_string(f)
        buff = StringIO(raw_string)
        encoding = read_unsigned_int(buff)
        num_entries = read_unsigned_int(buff)
        self._callback.start_set(self._key, num_entries, self._expiry, info={'encoding':'intset', 'sizeof_value':len(raw_string)})
        for x in xrange(0, num_entries) :
            if encoding == 8 :
                entry = read_unsigned_long(buff)
            elif encoding == 4 :
                entry = read_unsigned_int(buff)
            elif encoding == 2 :
                entry = read_unsigned_short(buff)
            else :
                raise Exception('read_intset', 'Invalid encoding %d for key %s' % (encoding, self._key))
            self._callback.sadd(self._key, entry)
        self._callback.end_set(self._key)

    def read_ziplist(self, f) :
        raw_string = self.read_string(f)
        buff = StringIO(raw_string)
        zlbytes = read_unsigned_int(buff)
        tail_offset = read_unsigned_int(buff)
        num_entries = read_unsigned_short(buff)
        self._callback.start_list(self._key, num_entries, self._expiry, info={'encoding':'ziplist', 'sizeof_value':len(raw_string)})
        for x in xrange(0, num_entries) :
            val = self.read_ziplist_entry(buff)
            self._callback.rpush(self._key, val)
        zlist_end = read_unsigned_char(buff)
        if zlist_end != 255 : 
            raise Exception('read_ziplist', "Invalid zip list end - %d for key %s" % (zlist_end, self._key))
        self._callback.end_list(self._key)

    def read_zset_from_ziplist(self, f) :
        raw_string = self.read_string(f)
        buff = StringIO(raw_string)
        zlbytes = read_unsigned_int(buff)
        tail_offset = read_unsigned_int(buff)
        num_entries = read_unsigned_short(buff)
        if (num_entries % 2) :
            raise Exception('read_zset_from_ziplist', "Expected even number of elements, but found %d for key %s" % (num_entries, self._key))
        num_entries = num_entries /2
        self._callback.start_sorted_set(self._key, num_entries, self._expiry, info={'encoding':'ziplist', 'sizeof_value':len(raw_string)})
        for x in xrange(0, num_entries) :
            member = self.read_ziplist_entry(buff)
            score = self.read_ziplist_entry(buff)
            if isinstance(score, str) :
                score = float(score)
            self._callback.zadd(self._key, score, member)
        zlist_end = read_unsigned_char(buff)
        if zlist_end != 255 : 
            raise Exception('read_zset_from_ziplist', "Invalid zip list end - %d for key %s" % (zlist_end, self._key))
        self._callback.end_sorted_set(self._key)

    def read_hash_from_ziplist(self, f) :
        raw_string = self.read_string(f)
        buff = StringIO(raw_string)
        zlbytes = read_unsigned_int(buff)
        tail_offset = read_unsigned_int(buff)
        num_entries = read_unsigned_short(buff)
        if (num_entries % 2) :
            raise Exception('read_hash_from_ziplist', "Expected even number of elements, but found %d for key %s" % (num_entries, self._key))
        num_entries = num_entries /2
        self._callback.start_hash(self._key, num_entries, self._expiry, info={'encoding':'ziplist', 'sizeof_value':len(raw_string)})
        for x in xrange(0, num_entries) :
            field = self.read_ziplist_entry(buff)
            value = self.read_ziplist_entry(buff)
            self._callback.hset(self._key, field, value)
        zlist_end = read_unsigned_char(buff)
        if zlist_end != 255 : 
            raise Exception('read_hash_from_ziplist', "Invalid zip list end - %d for key %s" % (zlist_end, self._key))
        self._callback.end_hash(self._key)
    
    
    def read_ziplist_entry(self, f) :
        length = 0
        value = None
        prev_length = read_unsigned_char(f)
        if prev_length == 254 :
            prev_length = read_unsigned_int(f)
        entry_header = read_unsigned_char(f)
        if (entry_header >> 6) == 0 :
            length = entry_header & 0x3F
            value = f.read(length)
        elif (entry_header >> 6) == 1 :
            length = ((entry_header & 0x3F) << 8) | read_unsigned_char(f)
            value = f.read(length)
        elif (entry_header >> 6) == 2 :
            length = read_unsigned_int(f)
            value = f.read(length)
        elif (entry_header >> 4) == 12 :
            value = read_signed_short(f)
        elif (entry_header >> 4) == 13 :
            value = read_signed_int(f)
        elif (entry_header >> 4) == 14 :
            value = read_signed_long(f)
        elif (entry_header == 240) :
            value = read_24bit_signed_number(f)
        elif (entry_header == 254) :
            value = read_signed_char(f)
        elif (entry_header >= 241 and entry_header <= 253) :
            value = entry_header - 241
        else :
            raise Exception('read_ziplist_entry', 'Invalid entry_header %d for key %s' % (entry_header, self._key))
        return value
        
    def read_zipmap(self, f) :
        raw_string = self.read_string(f)
        buff = io.BytesIO(bytearray(raw_string))
        num_entries = read_unsigned_char(buff)
        self._callback.start_hash(self._key, num_entries, self._expiry, info={'encoding':'zipmap', 'sizeof_value':len(raw_string)})
        while True :
            next_length = self.read_zipmap_next_length(buff)
            if next_length is None :
                break
            key = buff.read(next_length)
            next_length = self.read_zipmap_next_length(buff)
            if next_length is None :
                raise Exception('read_zip_map', 'Unexepcted end of zip map for key %s' % self._key)        
            free = read_unsigned_char(buff)
            value = buff.read(next_length)
            try:
                value = int(value)
            except ValueError:
                pass
            
            skip(buff, free)
            self._callback.hset(self._key, key, value)
        self._callback.end_hash(self._key)

    def read_zipmap_next_length(self, f) :
        num = read_unsigned_char(f)
        if num < 254:
            return num
        elif num == 254:
            return read_unsigned_int(f)
        else:
            return None

    def verify_magic_string(self, magic_string) :
        if magic_string != 'REDIS' :
            raise Exception('verify_magic_string', 'Invalid File Format')

    def verify_version(self, version_str) :
        version = int(version_str)
        if version < 1 or version > 6 : 
            raise Exception('verify_version', 'Invalid RDB version number %d' % version)

    def init_filter(self, filters):
        self._filters = {}
        if not filters:
            filters={}

        if not 'dbs' in filters:
            self._filters['dbs'] = None
        elif isinstance(filters['dbs'], int):
            self._filters['dbs'] = (filters['dbs'], )
        elif isinstance(filters['dbs'], list):
            self._filters['dbs'] = [int(x) for x in filters['dbs']]
        else:
            raise Exception('init_filter', 'invalid value for dbs in filter %s' %filters['dbs'])
        
        if not ('keys' in filters and filters['keys']):
            self._filters['keys'] = re.compile(".*")
        else:
            self._filters['keys'] = re.compile(filters['keys'])

        if not 'types' in filters:
            self._filters['types'] = ('set', 'hash', 'sortedset', 'string', 'list')
        elif isinstance(filters['types'], str):
            self._filters['types'] = (filters['types'], )
        elif isinstance(filters['types'], list):
            self._filters['types'] = [str(x) for x in filters['types']]
        else:
            raise Exception('init_filter', 'invalid value for types in filter %s' %filters['types'])
        
    def matches_filter(self, db_number, key=None, data_type=None):
        if self._filters['dbs'] and (not db_number in self._filters['dbs']):
            return False
        if key and (not self._filters['keys'].match(str(key))):
            return False

        if data_type is not None and (not self.get_logical_type(data_type) in self._filters['types']):
            return False
        return True
    
    def get_logical_type(self, data_type):
        return DATA_TYPE_MAPPING[data_type]
        
    def lzf_decompress(self, compressed, expected_length):
        in_stream = bytearray(compressed)
        in_len = len(in_stream)
        in_index = 0
        out_stream = bytearray()
        out_index = 0
    
        while in_index < in_len :
            ctrl = in_stream[in_index]
            if not isinstance(ctrl, int) :
                raise Exception('lzf_decompress', 'ctrl should be a number %s for key %s' % (str(ctrl), self._key))
            in_index = in_index + 1
            if ctrl < 32 :
                for x in xrange(0, ctrl + 1) :
                    out_stream.append(in_stream[in_index])
                    #sys.stdout.write(chr(in_stream[in_index]))
                    in_index = in_index + 1
                    out_index = out_index + 1
            else :
                length = ctrl >> 5
                if length == 7 :
                    length = length + in_stream[in_index]
                    in_index = in_index + 1
                
                ref = out_index - ((ctrl & 0x1f) << 8) - in_stream[in_index] - 1
                in_index = in_index + 1
                for x in xrange(0, length + 2) :
                    out_stream.append(out_stream[ref])
                    ref = ref + 1
                    out_index = out_index + 1
        if len(out_stream) != expected_length :
            raise Exception('lzf_decompress', 'Expected lengths do not match %d != %d for key %s' % (len(out_stream), expected_length, self._key))
        return str(out_stream)

def skip(f, free):
    if free :
        f.read(free)

def ntohl(f) :
    val = read_unsigned_int(f)
    new_val = 0
    new_val = new_val | ((val & 0x000000ff) << 24)
    new_val = new_val | ((val & 0xff000000) >> 24)
    new_val = new_val | ((val & 0x0000ff00) << 8)
    new_val = new_val | ((val & 0x00ff0000) >> 8)
    return new_val

def to_datetime(usecs_since_epoch):
    seconds_since_epoch = usecs_since_epoch / 1000000
    useconds = usecs_since_epoch % 1000000
    dt = datetime.datetime.utcfromtimestamp(seconds_since_epoch)
    delta = datetime.timedelta(microseconds = useconds)
    return dt + delta
    
def read_signed_char(f) :
    return struct.unpack('b', f.read(1))[0]
    
def read_unsigned_char(f) :
    return struct.unpack('B', f.read(1))[0]

def read_signed_short(f) :
    return struct.unpack('h', f.read(2))[0]
        
def read_unsigned_short(f) :
    return struct.unpack('H', f.read(2))[0]

def read_signed_int(f) :
    return struct.unpack('i', f.read(4))[0]
    
def read_unsigned_int(f) :
    return struct.unpack('I', f.read(4))[0]

def read_24bit_signed_number(f):
    s = '0' + f.read(3)
    num = struct.unpack('i', s)[0]
    return num >> 8
    
def read_signed_long(f) :
    return struct.unpack('q', f.read(8))[0]
    
def read_unsigned_long(f) :
    return struct.unpack('Q', f.read(8))[0]

def string_as_hexcode(string) :
    for s in string :
        if isinstance(s, int) :
            print(hex(s))
        else :
            print(hex(ord(s)))

