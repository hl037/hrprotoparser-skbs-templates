## from itertools import chain
import struct
from itertools import chain

class Type(object):
  def set(self, val):
    """@return a handler (default implementation returns `py_val`) for later call to `self.get(handler)`.
    Should also do the type checking"""
    self.val = val

  def get(self):
    """@return a python object corresponding to the handler. The default implementation returns handler"""
    return self.val

  def encode(self):
    self.struct.pack(*self.get_flat())

  def decode(self, b):
    self.set_flat(self.struct.unpack(b))

  def set_flat(self, val):
    self.val, = val

  def get_flat(self):
    return self.val,

  @property
  def struct(self):
    raise NotImplementedError()

  @property
  def size(self):
    raise NotImplementedError()

  @property
  def nval(self):
    raise NotImplementedError()

## for name, size, fmt, init in chain(_p.int_types, _p.uint_types, _p.float_types) :
class {{name}}(Type):
  """
  Represent a {{name}}
  """
  def __init__(self):
    self.val = {{init}}
  struct = struct.Struct('{{fmt}}')
  size = {{size}}
  nval = 1
## -

arrayTypes = { k : None for k in types.keys() }

class Array(Type):
  """
  Class to represent a C array
  """
  def __init_subclass__(cls, /, type, n, **kwargs):
    cls.type = type
    cls.n = n
    cls.struct = struct.Struct(type.format * n)
    super().__init_subclass__(**kwargs)
  
  def __init__(self):
    self.val = [ self.type() for _ in range(self.n) ]

  def set(self, val, deep=True):
    if len(val) != self.n) :
      raise ValueError(f'Inconsistent array size : {len(self.val)=} != {len(val)=}')
    if deep :
      for v, nv in zip(self.val, nval) :
        v.set(nv)
    else:
      self.val = val

  def get_flat(self):
    return chain(v.get_flat() for v in self.val)

  def set_flat(self, val):
    nval = self.type.nval
    for i, v in enumerate(self.val) :
      v.set_flat(val[i * nval:(i + 1) * nval])

  cache = {}

  @classmethod
  def new(cls, type, n):
    T = cache.get((type, n), None)
    if T is None :
      class Array_(cls, type=type, n=n):
        pass
      T = Array_
      cls.cache[(type, n)] = t
    return T()

class VarLenArray():
  """
  Class to represent a C varlen array
  """
  def resize(self, n):
    self.n = n
    self.struct = struct.Struct(self.type.format * n)
    self.__init__()

  @classmethod
  def new(cls, type):
    T = cache.get((type, 0), None)
    if T is None :
      class Array_(cls, Array, type=type, n=0):
        pass
      T = Array_
      cls.cache[(type, 0)] = t
    return T()
    

class Fields(object):
  pass
    
class Struct(Type):
  """
  Class to represent a C struct
  """
  def __init__(self):
    self.val = self

  def set(self, val, deep=True):
    if isinstance(val, tuple) or isinstance(val, list) :
      return self.setFromIterable(val)
    if deep :
      return self.copyFrom(val)
    if isinstance(val, self.__class__) :
      self.val = val
  
  def setFromIterable(self, val):
    for f, v in zip(self.fields, val) :
      f.set(val)

  def copyFrom(self, val):
    raise NotImplementedError()

  def get_flat(self):
    raise NotImplementedError()

  def set_flat(self, val):
    raise NotImplementedError()

  @property
  def fields(self):
    raise NotImplementedError()
    

class Packet():
  """
  Class to reprensent a packet
  """
  pass


## for s in chain(_p.proto.S, _p.proto.P) :
## sname = _p.struct_name(s)
## sizeof_s, varlen_t = _p.sizeof2(s)
## if varlen_t is not None:
##   sizeof_varlen_t = _p.sizeof(varlen_t)
## -

class {{sname}}(Struct):
  _fields = Fields()
##   for f in s.fields
  _fields.{{f.name}} = {{getPyType(f)}}
  @property
  def {{f.name}}(self):
    _fields.{{f.name}}.get()
    
  @{{f.name}}.setter
  def {{f.name}}(self, val):
    _fields.{{f.name}}.set(val)

## -
  



      
    


