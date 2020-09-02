"""
hrpotoparser Python plugin.
"""

try:
  inside_skbs_plugin
except:
  from skbs.pluginutils import IsNotAModuleOrScriptError
  raise IsNotAModuleOrScriptError

conf = C(
  #   Predefined template syntax are Tempiny.PY, Tempiny.C and Tempiny.TEX :
  #   Tempiny.C  = dict(stmt_line_start=r'//#', begin_expr='{{', end_expr='}})
  #   Tempiny.PY = dict(stmt_line_start=r'##', begin_expr='{{', end_expr='}}')
  #   Tempiny.TEX = dict(stmt_line_start=r'%#', begin_expr='<<', end_expr='>>')
  tempiny = [
    ('*' , Tempiny.PY)
  ],
  opt_prefix = '_opt.',
  force_prefix = '_force.',
  raw_prefix = '_raw.',
  template_prefix = '_template.',
  #   pathmod_filename = '__pathmod',
)
conf.dir_template_filename = conf.template_prefix

from hrprotoparser.cli import hrprotoparser_cmd
import hrprotoparser.protocol_parser as hrpp

plugin = C()
p = plugin

# Put above additionnal options / arguments
@hrprotoparser_cmd()
def hrpp_cli(**kwargs):
  """
  hrpotoparser Python plugin.
  """
  plugin.update(kwargs)


invokeCmd(hrpp_cli, args)

def export(f):
  plugin[f.__name__] = f
  return f

c_types = {
  'int8'  : ('int8_t', 1),
  'char'  : ('char', 1),
  'uint8' : ('uint8_t', 1),
  'byte'  : ('unsigned char', 1),
  'int16' : ('int16_t', 2),
  'uint16': ('uint16_t', 2),
  'int32' : ('int32_t', 4),
  'uint32': ('uint32_t', 4),
  'int64' : ('int64_t', 8),
  'uint64': ('uint64_t', 8),
  'float' : ('float', 4),
  'double': ('double', 8),
  'usize' : ('size_t', None),
  'size'  : ('ssize_t', None),
}
plugin.c_types = c_types

int_types = (
    ('Int8', 1, 'b', '0'),
    ('Int16', 2, 'h', '0'),
    ('Int32', 4, 'i', '0'),
    ('Int64', 8, 'q', '0'),
)
plugin.int_types = int_types
uint_types = (
    ('UInt8', 1, 'B', '0'),
    ('UInt16', 2, 'H', '0'),
    ('UInt32', 4, 'I', '0'),
    ('UInt64', 8, 'Q', '0'),
)
plugin.uint_types = uint_types
float_types = (
    ('Float', 4, 'f', '0.'),
    ('Double', 8, 'd', '0.'),
)
plugin.float_types = float_types

py_types = {
  'int8'  : 'Int8',
  'char'  : 'Int8',
  'uint8' : 'UInt8',
  'byte'  : 'UInt8',
  'int16' : 'Int16',
  'uint16': 'UInt16',
  'int32' : 'Int32',
  'uint32': 'UInt32',
  'int64' : 'Int64',
  'uint64': 'UInt64',
  'float' : 'Float',
  'double': 'Double',
  'usize' : 'UInt64',
  'size'  : 'Int64',
}

py_struct_fmt = {
  'int8'  : 'b',
  'char'  : 'b',
  'uint8' : 'B',
  'byte'  : 'B',
  'int16' : 'h',
  'uint16': 'H',
  'int32' : 'i',
  'uint32': 'I',
  'int64' : 'q',
  'uint64': 'Q',
  'float' : 'f',
  'double': 'd',
  'usize' : 'Q',
  'size'  : 'q',
}
plugin.py_types = py_types

@export
def cName(s):
  n = s.name
  r = n[0].lower()
  for c in n[1:]:
    if c.isupper():
      r += '_'+c.lower()
    else:
      r += c
  return r


@export
def struct_name(s):
  return s.name
  
@export
def getPyType(f):
  t = f.type
  a_begin = ''
  a_end = ''
  flexible = False;
  while t.order == hrpp.Array.order:
    if t.nb is None:
      flexible = True
      a_begin = a_begin + 'VarLenArray.get_class('
      a_end = ')' + a_end
    else:
      a_begin = a_begin + 'Array.get_class('
      a_end = f', {t.nb.name if t.nb.kind is hrpp.Constant.NAMED else str(t.nb.computed)})' + a_end
    t = t.t
  if t.order == hrpp.Enum.order:
    t = t.type
  if t.order == hrpp.Builtin.order:
    tt = py_types[t.name]
  else:
    tt = struct_name(t)
  return a_begin + tt + a_end

@export
def comment(f):
  if f.comment is None:
    return ''
  else:
    return '// ' + f.comment

@export
def addStruct(s):
  exec(struct_code)

@export
def structArg(f):
  t = f.type
  if t.order == hrpp.Enum.order:
    t = t.type
  if t.order == hrpp.Builtin.order:
    return f.name
  if t.order == hrpp.Array.order:
    if t.t.name =='char':
      return f.name
  return '*'+f.name

@export
def sizeof4(t):
  """
  @return (sizeof(t), type of last variable len type if any, nb_field_total, fmt)
  """
  if t.order == hrpp.Builtin.order:
    return (c_types[t.name][1], None, 1, py_struct_fmt[t.name])
  if t.order == hrpp.Array.order:
    if t.nb is None:
      return (0, t.t, 0, '')
    size, varlen_t, nv, fmt = sizeof4(t.t)
    if varlen_t is not None:
      raise RuntimeError('Array of varlen Struct')
    nb = t.nb.computed
    return (nb * size, varlen_t, nb * nv, nb * fmt)
  if t.order == hrpp.Struct.order or t.order == hrpp.Packet.order:
    fields = [ sizeof4(f.type) for f in t.fields ]
    #print(s)
    if len(fields) == 0:
      return (0, None, 0, '')
    if any( (varlen_t is not None) for _, varlen_t, _, _ in fields[:-1] ):
      raise RuntimeError('Struct with varlen field not at end')
    return (
      sum(s   for s, _, _,  _ in fields),
      fields[-1][1],
      sum(nv  for _, _, nv, _ in fields),
      ''.join( fmt for _, _, _,  fmt in fields ),
    )
  if t.order == hrpp.Enum.order:
    return sizeof4(t.type)
  if t.order == hrpp.Alias.order:
    return sizeof4(t.alias)
  raise NotImplementedError(f'self.order === {t.order} is not handled')

@export
def sizeof2(t):
  return sizeof4(t)[:2]

@export
def sizeof(t):
  return sizeof2(t)[0]

def _varlen_field(t, name):
  if t.order == hrpp.Builtin.order:
    raise ValueError(f'type "{t.name}" has no variable fields')
  if t.order == hrpp.Array.order:
    if t.nb is None :
      return name
    else:
      raise ValueError(f'type "{t.name}" has no variable fields')
  if t.order == hrpp.Struct.order or t.order == hrpp.Packet.order:
    f = t.fields[-1]
    return _varlen_field(f.type, name + f'.{f.name}')
  if t.order == hrpp.Enum.order:
    return _varlen_field(t.type)
  if t.order == hrpp.Alias.order:
    return _varlen_field(t.alias)
  raise NotImplementedError(f'self.order === {t.order} is not handled')

  

@export
def varlen_field(t):
  return _varlen_field(t, '')[1:]

@export
def lastRecType(s):
  d = 0
  f = s.fields[-1].name
  t = s.fields[-1].type
  while t.order != hrpp.Array.order:
    if t.order == hrpp.Builtin.order or t.order == hrpp.Enum.order:
      raise RuntimeError()
    if t.order == hrpp.Alias.order:
      t = t.alias
      continue
    else:
      d += 1
      t = t.fields[-1].type
  if t.nb is not None:
    raise RuntimeError()
  return (t.t, f + '[-1]' * d)

_psize_levels = [ 2**(7*i)-i for i in range(1, 10) ]

@export
def compute_total_size(base_size):
  return base_size + next( i for i , v in enumerate(_psize_levels, 1) if base_size < v )

@export
def encode_varint(i):
  l = []
  while i :
    l.append((i & 0b_0111_1111) | 0b_1000_0000)
    i >>= 7
  l[-1] &= 0b_0111_1111
  return bytes(l)

@export
def bool(v):
  return v.lower() in ('1', 'true', 'yes', 'y')


@export
def is_aliased_packet(s):
  if s.order != hrpp.Alias.order :
    return False
  while s.order == hrpp.Alias.order :
    s = s.alias
  return s.order == hrpp.Packet.order


