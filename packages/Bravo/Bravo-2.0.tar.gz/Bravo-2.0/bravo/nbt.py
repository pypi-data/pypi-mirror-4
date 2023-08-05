from struct import Struct, error as StructError
from gzip import GzipFile
from UserDict import DictMixin

from bravo.errors import MalformedFileError

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10

class TAG(object):
    """Each Tag needs to take a file-like object for reading and writing.
    The file object will be initialised by the calling code."""
    id = None

    def __init__(self, value=None, name=None):
        self.name = name
        self.value = value

    #Parsers and Generators
    def _parse_buffer(self, buffer):
        raise NotImplementedError(self.__class__.__name__)

    def _render_buffer(self, buffer, offset=None):
        raise NotImplementedError(self.__class__.__name__)

    #Printing and Formatting of tree
    def tag_info(self):
        return self.__class__.__name__ + \
               ('("%s")'%self.name if self.name else "") + \
               ": " + self.__repr__()

    def pretty_tree(self, indent=0):
        return ("\t"*indent) + self.tag_info()

class _TAG_Numeric(TAG):
    def __init__(self, value=None, name=None, buffer=None):
        super(_TAG_Numeric, self).__init__(value, name)
        self.size = self.fmt.size
        if buffer:
            self._parse_buffer(buffer)

    #Parsers and Generators
    def _parse_buffer(self, buffer, offset=None):
        self.value = self.fmt.unpack(buffer.read(self.size))[0]

    def _render_buffer(self, buffer, offset=None):
        buffer.write(self.fmt.pack(self.value))

    #Printing and Formatting of tree
    def __repr__(self):
        return str(self.value)

#== Value Tags ==#
class TAG_Byte(_TAG_Numeric):
    id = TAG_BYTE
    fmt = Struct(">b")

class TAG_Short(_TAG_Numeric):
    id = TAG_SHORT
    fmt = Struct(">h")

class TAG_Int(_TAG_Numeric):
    id = TAG_INT
    fmt = Struct(">i")

class TAG_Long(_TAG_Numeric):
    id = TAG_LONG
    fmt = Struct(">q")

class TAG_Float(_TAG_Numeric):
    id = TAG_FLOAT
    fmt = Struct(">f")

class TAG_Double(_TAG_Numeric):
    id = TAG_DOUBLE
    fmt = Struct(">d")

class TAG_Byte_Array(TAG):
    id = TAG_BYTE_ARRAY
    def __init__(self, buffer=None):
        super(TAG_Byte_Array, self).__init__()
        self.value = ''
        if buffer:
            self._parse_buffer(buffer)

    #Parsers and Generators
    def _parse_buffer(self, buffer, offset=None):
        length = TAG_Int(buffer=buffer)
        self.value = buffer.read(length.value)

    def _render_buffer(self, buffer, offset=None):
        length = TAG_Int(len(self.value))
        length._render_buffer(buffer, offset)
        buffer.write(self.value)

    #Printing and Formatting of tree
    def __repr__(self):
        return "[%i bytes]" % len(self.value)

class TAG_String(TAG):
    id = TAG_STRING
    def __init__(self, value=None, name=None, buffer=None):
        super(TAG_String, self).__init__(value, name)
        if buffer:
            self._parse_buffer(buffer)

    #Parsers and Generators
    def _parse_buffer(self, buffer, offset=None):
        length = TAG_Short(buffer=buffer)
        read = buffer.read(length.value)
        if len(read) != length.value:
            raise StructError()
        self.value = unicode(read, "utf-8")

    def _render_buffer(self, buffer, offset=None):
        save_val = self.value.encode("utf-8")
        length = TAG_Short(len(save_val))
        length._render_buffer(buffer, offset)
        buffer.write(save_val)

    #Printing and Formatting of tree
    def __repr__(self):
        return self.value

#== Collection Tags ==#
class TAG_List(TAG):
    id = TAG_LIST
    def __init__(self, type=None, value=None, name=None, buffer=None):
        super(TAG_List, self).__init__(value, name)
        if type:
            self.tagID = type.id
        else: self.tagID = None
        self.tags = []
        if buffer:
            self._parse_buffer(buffer)
        if not self.tagID:
            raise ValueError("No type specified for list")

    #Parsers and Generators
    def _parse_buffer(self, buffer, offset=None):
        self.tagID = TAG_Byte(buffer=buffer).value
        self.tags = []
        length = TAG_Int(buffer=buffer)
        for x in range(length.value):
            self.tags.append(TAGLIST[self.tagID](buffer=buffer))

    def _render_buffer(self, buffer, offset=None):
        TAG_Byte(self.tagID)._render_buffer(buffer, offset)
        length = TAG_Int(len(self.tags))
        length._render_buffer(buffer, offset)
        for i, tag in enumerate(self.tags):
            if tag.id != self.tagID:
                raise ValueError("List element %d(%s) has type %d != container type %d" %
                         (i, tag, tag.id, self.tagID))
            tag._render_buffer(buffer, offset)

    #Printing and Formatting of tree
    def __repr__(self):
        return "%i entries of type %s" % (len(self.tags), TAGLIST[self.tagID].__name__)

    def pretty_tree(self, indent=0):
        output = [super(TAG_List,self).pretty_tree(indent)]
        if len(self.tags):
            output.append(("\t"*indent) + "{")
            output.extend([tag.pretty_tree(indent+1) for tag in self.tags])
            output.append(("\t"*indent) + "}")
        return '\n'.join(output)

class TAG_Compound(TAG, DictMixin):
    id = TAG_COMPOUND
    def __init__(self, buffer=None):
        super(TAG_Compound, self).__init__()
        self.tags = []
        if buffer:
            self._parse_buffer(buffer)

    #Parsers and Generators
    def _parse_buffer(self, buffer, offset=None):
        while True:
            type = TAG_Byte(buffer=buffer)
            if type.value == TAG_END:
                #print "found tag_end"
                break
            else:
                name = TAG_String(buffer=buffer).value
                try:
                    #DEBUG print type, name
                    tag = TAGLIST[type.value](buffer=buffer)
                    tag.name = name
                    self.tags.append(tag)
                except KeyError:
                    raise ValueError("Unrecognised tag type")

    def _render_buffer(self, buffer, offset=None):
        for tag in self.tags:
            TAG_Byte(tag.id)._render_buffer(buffer, offset)
            TAG_String(tag.name)._render_buffer(buffer, offset)
            tag._render_buffer(buffer,offset)
        buffer.write('\x00') #write TAG_END

    # Dict compatibility.
    # DictMixin requires at least __getitem__, and for more functionality,
    # __setitem__, __delitem__, and keys.

    def __getitem__(self, key):
        if isinstance(key,int):
            return self.tags[key]
        elif isinstance(key, str):
            for tag in self.tags:
                if tag.name == key:
                    return tag
            else:
                raise KeyError("A tag with this name does not exist")
        else:
            raise ValueError("key needs to be either name of tag, or index of tag")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            # Just try it. The proper error will be raised if it doesn't work.
            self.tags[key] = value
        elif isinstance(key, str):
            value.name = key
            for i, tag in enumerate(self.tags):
                if tag.name == key:
                    self.tags[i] = value
                    return
            self.tags.append(value)

    def __delitem__(self, key):
        if isinstance(key, int):
            self.tags = self.tags[:key] + self.tags[key:]
        elif isinstance(key, str):
            for i, tag in enumerate(self.tags):
                if tag.name == key:
                    self.tags = self.tags[:i] + self.tags[i:]
                    return
            raise KeyError("A tag with this name does not exist")
        else:
            raise ValueError("key needs to be either name of tag, or index of tag")

    def keys(self):
        return [tag.name for tag in self.tags]


    #Printing and Formatting of tree
    def __repr__(self):
        return '%i Entries' % len(self.tags)

    def pretty_tree(self, indent=0):
        output = [super(TAG_Compound,self).pretty_tree(indent)]
        if len(self.tags):
            output.append(("\t"*indent) + "{")
            output.extend([tag.pretty_tree(indent+1) for tag in self.tags])
            output.append(("\t"*indent) + "}")
        return '\n'.join(output)


TAGLIST = {TAG_BYTE:TAG_Byte, TAG_SHORT:TAG_Short, TAG_INT:TAG_Int, TAG_LONG:TAG_Long, TAG_FLOAT:TAG_Float, TAG_DOUBLE:TAG_Double, TAG_BYTE_ARRAY:TAG_Byte_Array, TAG_STRING:TAG_String, TAG_LIST:TAG_List, TAG_COMPOUND:TAG_Compound}

class NBTFile(TAG_Compound):
    """Represents an NBT file object"""

    def __init__(self, filename=None, mode=None, buffer=None, fileobj=None):
        super(NBTFile,self).__init__()
        self.__class__.__name__ = "TAG_Compound"
        self.filename = filename
        self.type = TAG_Byte(self.id)
        #make a file object
        if filename:
            self.file = GzipFile(filename, mode)
        elif buffer:
            self.file = buffer
        elif fileobj:
            self.file = GzipFile(fileobj=fileobj)
        else:
            self.file = None
        #parse the file given intitially
        if self.file:
            self.parse_file()
            if filename and 'close' in dir(self.file):
                self.file.close()
            self.file = None

    def parse_file(self, filename=None, buffer=None, fileobj=None):
        if filename:
            self.file = GzipFile(filename, 'rb')
        elif buffer:
            self.file = buffer
        elif fileobj:
            self.file = GzipFile(fileobj=fileobj)
        if self.file:
            try:
                type = TAG_Byte(buffer=self.file)
                if type.value == self.id:
                    name = TAG_String(buffer=self.file).value
                    self._parse_buffer(self.file)
                    self.name = name
                    self.file.close()
                else:
                    raise MalformedFileError("First record is not a Compound Tag")
            except StructError:
                raise MalformedFileError("Partial File Parse: file possibly truncated.")
        else: ValueError("need a file!")

    def write_file(self, filename=None, buffer=None, fileobj=None):
        if buffer:
            self.file = buffer
        elif filename:
            self.file = GzipFile(filename, "wb")
        elif fileobj:
            self.file = GzipFile(fileobj=fileobj)
        elif self.filename:
            self.file = GzipFile(self.filename, "wb")
        elif not self.file:
            raise ValueError("Need to specify either a filename or a file")
        #Render tree to file
        TAG_Byte(self.id)._render_buffer(self.file)
        TAG_String(self.name)._render_buffer(self.file)
        self._render_buffer(self.file)
        #make sure the file is complete
        if 'flush' in dir(self.file):
            self.file.flush()
        if filename and 'close' in dir(self.file):
            self.file.close()

# Useful utility functions for handling large NBT structures elegantly and
# Pythonically.

def unpack_nbt(tag):
    """
    Unpack an NBT tag into a native Python data structure.
    """

    if isinstance(tag, TAG_List):
        return [unpack_nbt(i) for i in tag.tags]
    elif isinstance(tag, TAG_Compound):
        return dict((i.name, unpack_nbt(i)) for i in tag.tags)
    else:
        return tag.value

def pack_nbt(s):
    """
    Pack a native Python data structure into an NBT tag. Only the following
    structures and types are supported:

     * int
     * float
     * str
     * unicode
     * dict

    Additionally, arbitrary iterables are supported.

    Packing is not lossless. In order to avoid data loss, TAG_Long and
    TAG_Double are preferred over the less precise numerical formats.

    Lists and tuples may become dicts on unpacking if they were not homogenous
    during packing, as a side-effect of NBT's format. Nothing can be done
    about this.

    Only strings are supported as keys for dicts and other mapping types. If
    your keys are not strings, they will be coerced. (Resistance is futile.)
    """

    if isinstance(s, int):
        return TAG_Long(s)
    elif isinstance(s, float):
        return TAG_Double(s)
    elif isinstance(s, (str, unicode)):
        return TAG_String(s)
    elif isinstance(s, dict):
        tag = TAG_Compound()
        for k, v in s:
            v = pack_nbt(v)
            v.name = str(k)
            tag.tags.append(v)
        return tag
    elif hasattr(s, "__iter__"):
        # We arrive at a slight quandry. NBT lists must be homogenous, unlike
        # Python lists. NBT compounds work, but require unique names for every
        # entry. On the plus side, this technique should work for arbitrary
        # iterables as well.
        tags = [pack_nbt(i) for i in s]
        t = type(tags[0])
        # If we're homogenous...
        if all(t == type(i) for i in tags):
            tag = TAG_List(type=t)
            tag.tags = tags
        else:
            tag = TAG_Compound()
            for i, item in enumerate(tags):
                item.name = str(i)
            tag.tags = tags
        return tag
    else:
        raise ValueError("Couldn't serialise type %s!" % type(s))
