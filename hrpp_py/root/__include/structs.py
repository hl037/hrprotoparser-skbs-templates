## from itertools import chain
## import struct
##
## if psize:
##   _psize = struct.Struct('<' + {1 : 'B', 2: 'H', 4:'I', 8: 'Q'}[psize])
##   def encode_psize(s):
##     return _psize.pack(s)
##   -
## -
## elif psize == 0:
##   _psize = struct.Struct('<Q')
##   def encode_psize(s):
##     return _p.encode_varint(s)
##   -
## -
## if tsize:
##   _tsize = struct.Struct('<' + {1 : 'B', 2: 'H', 4:'I', 8: 'Q'}[tsize])
##   def encode_type(s):
##     return _tsize.pack(s)
##   -
## -
## else:
##   _tsize = struct.Struct('<Q')
##   def encode_type(s):
##     return _p.encode_varint(s)
##   -
## -

import struct
from itertools import chain
import types

## if psize:
_psize = struct.Struct('<{{ {1 : 'B', 2: 'H', 4:'I', 8: 'Q'}[psize] }}')
## -
## elif psize is None:
_psize = struct.Struct('<Q')

_psize_levels = {{repr([ 2**(7*i)-i for i in range(1, 10) ])}}

def compute_total_size(base_size):
  return base_size + next( i for i , v in enumerate(_psize_levels, 1) if base_size < v )

def encode_varint(i):
  l = []
  while i :
    l.append((i & 0b_0111_1111) | 0b_1000_0000)
    i >>= 7
  l[-1] &= 0b_0111_1111
  return bytes(l)

## -
## if tsize:
_tsize = struct.Struct('<{{ {1 : 'B', 2: 'H', 4:'I', 8: 'Q'}[tsize] }}')
## -
## else:
_tsize = struct.Struct('<Q')
## -




class Type(object):
  def __init__(self, val=None):
    if val is not None :
      self.set(val)
  
  def set(self, val):
    """@return a handler (default implementation returns `py_val`) for later call to `self.get(handler)`.
    Should also do the type checking"""
    self.val = val

  def get(self):
    """@return a python object corresponding to the handler. The default implementation returns handler"""
    return self.val

  def encode(self):
    return self.struct.pack(*self.get_flat())

  def decode(self, b):
    self.set_flat(self.struct.unpack(b))

  def set_flat(self, val):
    self.val, = val

  def get_flat(self):
    return self.val,
  
  def __valrepr__(self, *args, **kwargs):
    return self.__repr__(*args, **kwargs)

## for name, size, fmt, init in chain(_p.int_types, _p.uint_types, _p.float_types) :
class {{name}}(Type):
  """
  Represent a {{name}}
  """
  def __init__(self, val=None):
    if val is None :
      self.val = {{init}}
    else:
      self.val = val
  fmt = {{repr(fmt)}}
  struct = struct.Struct('<{{fmt}}')
  size = {{size}}
  nval = 1
  def __repr__(self, indent=0):
    return f'{{name}}({self.val})'
  def __valrepr__(self, indent=0):
    return repr(self.val)
## -

class Array(Type):
  """
  Class to represent a C array
  """
  def __init_subclass__(cls, /, abstract=False, type=None, n=None, **kwargs):
    if abstract :
      return
    elif any( arg is None for arg in (type, n)) :
      raise TypeError('Missing packet argument')
    cls.type = type
    cls.n = n
    cls.fmt = '<' + type.struct.format[1:] * n
    cls.struct = struct.Struct(cls.fmt)
    cls.size = type.size * n
    cls.nval = type.nval * n
    super().__init_subclass__(**kwargs)
  
  def __init__(self, *args, **kwargs):
    self.internal_val = [ self.type() for _ in range(self.n) ]
    self.val = self
    super().__init__(*args, **kwargs)

  def __repr__(self, indent=0):
    return (
        f'{self.type.__name__}[{self.n}]''{\n' + '  ' * (indent + 1) + 
        (',\n' + '  ' * (indent + 1)).join(v.__valrepr__(indent + 1) for v in self.internal_val) +
        '\n' + '  ' * indent + '}'
    )

  def set(self, val, deep=True):
    if len(val) > self.n:
      raise ValueError(f'Inconsistent array size : {len(self.val)=} > {len(val)=}')
    if deep :
      for v, nv in zip(self.internal_val, val) :
        v.set(nv)
    elif len(val) != self.n :
      raise ValueError(f'Inconsistent array size : {len(self.val)=} != {len(val)=}')
    elif any( not isinstance(v) for v in val ) :
      raise TypeError(f'At least one value in the iterable is not of type {self.type.__class__.__name___}')
    else:
      self.internal_val = val

  def get_flat(self):
    return chain.from_iterable(v.get_flat() for v in self.internal_val)

  def set_flat(self, val):
    nval = self.type.nval
    for i, v in enumerate(self.internal_val) :
      v.set_flat(val[i * nval:(i + 1) * nval])

  def __getitem__(self, k):
    return self.internal_val.__getitem__(k).get()

  def __setitem__(self, k, v):
    return self.internal_val.__getitem__(k).set(v)

  def __len__(self):
    return self.n

  cache = {}

  @classmethod
  def get_class(cls, type, n):
    T = cls.cache.get((type, n), None)
    if T is None :
      class Array_(cls, type=type, n=n):
        pass
      T = Array_
      cls.cache[(type, n)] = T
    return T
## if psize != 0:

class VarLenArray(Array, abstract=True):
  """
  Class to represent a C varlen array
  """
  def resize(self, n, init=True):
    if self.n == n :
      return
    self.n = n
    self.fmt = '<' + self.type.struct.format[1:] * n
    self.struct = struct.Struct(self.fmt)
    self.size = self.type.size * n
    self.nval = self.type.nval * n
    if init :
      delta = n - len(self.internal_val)
      if delta > 0 :
        self.internal_val = list(chain(self.internal_val, ( self.type() for _ in range(delta) )))
      else:
        self.internal_val = self.internal_val[:delta]

  @classmethod
  def get_class(cls, type):
    T = cls.cache.get((type, 0), None)
    if T is None :
      class Array_(cls, Array, type=type, n=0):
        pass
      T = Array_
      cls.cache[(type, 0)] = T
    return T
    
  def set(self, val, deep=True):
    if not deep :
      if any( not isinstance(v) for v in val ) :
        raise TypeError(f'At least one value in the iterable is not of type {self.type.__class__.__name___}')
      else:
        self.resize(len(val), init=False)
        self.internal_val = val
      return
    else:
      self.resize(len(val))
      super().set(val, deep)
## -

  def decode(self, b):
    varlen_size = len(b)
    self.varlen_field.resize(varlen_size // self.type.size)
    return super().decode(b)

class Fields(object):
  pass
    
class Struct(Type):
  """
  Class to represent a C struct
  """
  def __init__(self, *args, **kwargs):
    self.val = self
    super().__init__(*args, **kwargs)

  def set(self, val, deep=True):
    if isinstance(val, tuple) or isinstance(val, list) :
      return self.setFromIterable(val)
    if isinstance(val, dict) :
      return self.setFromDict(val)
    if deep :
      return self.copyFrom(val)
    if isinstance(val, self.__class__) :
      self.val = val
  
  def setFromIterable(self, val):
    for f, v in zip(self._field_list, val) :
      f.set(v)

  def copyFrom(self, val):
    raise NotImplementedError()
  
  def copyFromDict(self, val):
    raise NotImplementedError()

  def get_flat(self):
    raise NotImplementedError()

  def set_flat(self, val):
    raise NotImplementedError()


class Packet():
  """
  Class to reprensent a packet
  """
  def __init_subclass__(cls, /, abstract=False, struct=None, header=None, size=None, type=None, **kwargs):
    if abstract :
      return
    elif any( arg is None for arg in (struct, header, size, type)) :
      raise TypeError('Missing packet argument')
    cls.struct = struct
    cls.header = header
    cls.size = size
    cls.type = type
    cls.header_len = len(header)
    cls._name = cls.__name__
    
  def __init__(self, data=None, ref=True):
    if data is None :
      self.data = self.struct()
    elif isinstance(data, self.struct) and ref :
      self.data = data
    else:
      self.data = self.struct(data)

  def encode(self):
    return self.header + self.data.encode()

  def decode(self, b):
    if b[:self.header_len] != self.header :
      raise ValueError('The byte stream passed is not compatible with this packet type')
    else:
      return self.data.decode(b[self.header_len:])
  
  @classmethod
  def new(cls, name, **kwargs) -> _typehint_Type_['__class__']:
    return types.new_class(name, (cls,), kwargs, None)

## if psize != 0:
class VarLenPacket(Packet, abstract=True):
  def __init_subclass__(cls, /, struct, header_type, type, **kwargs):
    cls.struct = struct
    cls.header_type = header_type
    cls.header_type_len = len(header_type)
    cls.type = type
    cls._name = cls.__name__

  @property
  def size(self):
##   if psize > 0:
    return {{psize}} + self.header_type_len + self.data.size
##   -
##   else:
    return compute_total_size(self.data.size + self.header_type_len)
##   -

  @property
  def header_size(self):
##   if psize > 0:
    return _psize.pack(self.size)
##   -
##   else:
    return encode_varint(self.size + self.header_type_len)
##   -

  @property
  def header(self):
    return self.header_size + self.header_type
## -
  
  
## for s in chain(_p.proto.S, _p.proto.P) :
##   sname = _p.struct_name(s)
##   sizeof_s, varlen_t, nval, fmt = _p.sizeof4(s)
##   if varlen_t is not None:
##     sizeof_varlen_t = _p.sizeof(varlen_t)
##   -
##
##   if s.order in (_p.Struct.order, _p.Packet.order) :
##
class {{sname}}(Struct):
  _fmt = '<{{fmt}}'
  _size = {{sizeof_s}}
  field_list = []
  _nval = {{nval}}
  _name = '{{sname}}'

  def __init__(self, *args, **kwargs):
    self._fields = Fields()
##     for f in s.fields:
    self._fields.{{f.name}} = {{_p.getPyType(f)}}()
##     -
    self._field_list = [
##     for f in s.fields:
      self._fields.{{f.name}},
##     -
    ]
    super().__init__(*args, **kwargs)
  
  # Fields

##     for f in s.fields:
  {{f.name}} = {{_p.getPyType(f)}}
  field_list.append({{f.name}})
  @property
  def {{f.name}}(self):
    return self._fields.{{f.name}}.get()
  @{{f.name}}.setter
  def {{f.name}}(self, val):
    self._fields.{{f.name}}.set(val)

##     -
  # Methods

  def __repr__(self, indent=0):
    return ('{{sname}}{'
##     for f in s.fields:
      + "\n" + '  ' * (indent + 1) + f"{{f.name}} = {self._fields.{{f.name}}.__valrepr__(indent + 1)}"
##     -
      + '\n' + '  ' * indent + '}'
    )

  def copyFrom(self, val):
##     for f in s.fields:
    self._fields.{{f.name}} = val.{{f.name}}
##     -
##     if len(s.fields) == 0:
    pass
##     -

  def copyFromDict(self, val):
##     for f in s.fields:
    self._fields.{{f.name}}.set(val['{{f.name}}'])
##     -
##     if len(s.fields) == 0:
    pass
##     -

  def get_flat(self):
    return chain(
##     for f in s.fields:
      self._fields.{{f.name}}.get_flat(),
##     -
    )

  def set_flat(self, val):
    i = 0
##     for f in s.fields:
    end = i + self._fields.{{f.name}}.nval
    self._fields.{{f.name}}.set_flat(val[i:end]),
    i = end
##     -

##     if varlen_t is None:
  fmt = _fmt
  struct = struct.Struct(fmt)
  size = _size
  nval = _nval
##     -
##     else:
  def decode(self, b):
    varlen_size = len(b) - self._size
    self.varlen_field.resize(varlen_size // self.varlen_field.type.size)
    return super().decode(b)

  @property
  def varlen_field(self):
    return self.{{_p.varlen_field(s)}}

  @property
  def fmt(self):
    return self._fmt + self.varlen_field.fmt[1:]

  @property
  def struct(self):
    return struct.Struct(self.fmt)
  
  @property
  def size(self):
    return self._size + self.varlen_field.size
  
  @property
  def nval(self):
    return self._nval + self.varlen_field.nval
##     -
##   -

## -


class Packets(object):
  _by_type = {}
## for s in _p.proto.P :
##   sname = _p.struct_name(s)
##   sizeof_s, varlen_t, nval, fmt = _p.sizeof4(s)
##   if varlen_t is not None:
##     sizeof_varlen_t = _p.sizeof(varlen_t)
##   -
##   if s.order == _p.Packet.order:
##     header_type = encode_type(s.type.computed)
##     if varlen_t is None:
##       if psize == 0:
##         s_psize = len(header_type) + sizeof_s
##         header_psize = b''
##       -
##       elif psize is None:
##         s_psize = _p.compute_total_size(len(header_type) + sizeof_s)
##         header_psize = _p.encode_varint(s_psize)
##       -
##       else:
##         s_psize = psize + len(header_type) + sizeof_s
##         header_psize = _psize.pack(s_psize)
##       -
##     header = header_psize + header_type
  {{sname}} = Packet.new({{repr(sname)}}, struct={{sname}}, header={{repr(header)}}, size={{s_psize}}, type={{s.type.computed}})
##     -
##     else:
  {{sname}} = VarLenPacket.new({{repr(sname)}}, struct={{sname}}, header_type={{repr(header_type)}}, type={{s.type.computed}})
##     -
##   -
##   elif _p.is_aliased_packet(s):
  {{sname}} = {{_p.struct_name(s.alias)}}
##   -
## -
## for s in _p.proto.P :
##   sname = _p.struct_name(s)
  _by_type[{{s.type.computed}}] = {{sname}}
## -
  def __getitem__(self, k):
    return self._by_type[k]

packets = Packets()

del Packets

