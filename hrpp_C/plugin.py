"""
hrpotoparser C plugin.
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
    ('*' , Tempiny.C)
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
@click.option('--parser/--no-parser', is_flag=True, default=True)
@click.option('--single-handler/--no-single-handler', is_flag=True, default=False)
@hrprotoparser_cmd()
def hrpp_cli(**kwargs):
  """
  hrpotoparser C plugin.
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
  return cName(s)
  
@export
def getCType(f):
  t = f.type
  a = ''
  flexible = False;
  close_parenthesis = ''
  while t.order == hrpp.Array.order:
    if t.nb is None:
      flexible = True
      close_parenthesis += ')'
    else:
      a = a + '[{}]'.format(t.nb.name if t.nb.kind is hrpp.Constant.NAMED else str(t.nb.computed)) # In C language, array length order is reversed (C uses order of the dimension, not type composition)
    t = t.t
  a += close_parenthesis
  if t.order == hrpp.Builtin.order:
    tt = c_types[t.name][0]
  elif t.order == hrpp.Struct.order or t.order == hrpp.Packet.order:
    tt = struct_name(t) + "_t"
  elif t.order == hrpp.Enum.order:
    tt = cName(t) + "_t"
  else:
    tt = t.name
  if flexible :
    tt = 'FLEXIBLE_ARRAY('+tt+','
  return tt, a


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
def sizeof2(t):
  """
  @return (sizeof(t), type of last variable len type if any)
  """
  if t.order == hrpp.Builtin.order:
    return (c_types[t.name][1], None)
  if t.order == hrpp.Array.order:
    if t.nb is None:
      return (0, t.t)
    size, varlen_t = sizeof2(t.t)
    if varlen_t is not None:
      raise RuntimeError('Array of varlen Struct')
    return (t.nb.computed * size, varlen_t)
  if t.order == hrpp.Struct.order or t.order == hrpp.Packet.order:
    fields = [ sizeof2(f.type) for f in t.fields ]
    #print(s)
    if len(fields) == 0:
      return (0, None)
    if any( (varlen_t is not None) for _, varlen_t in fields[:-1] ):
      raise RuntimeError('Struct with varlen field not at end')
    return (sum(s for s, _ in fields), fields[-1][1])
  if t.order == hrpp.Enum.order:
    return sizeof2(t.type)
  if t.order == hrpp.Alias.order:
    return sizeof2(t.alias)
  raise NotImplementedError('self.order === {} is not handled'.format(t.order))

@export
def sizeof(t):
  return sizeof2(t)[0]

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

@export
def bool(v):
  return v.lower() in ('1', 'true', 'yes', 'y')
