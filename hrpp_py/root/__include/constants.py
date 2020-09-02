
## for e in _p.proto.E:
##   if 'int' in e.type.name  :
class {{e.name}}(IntEnum):
##   -
##   elif e.type.name in ('float', 'double') :
class {{e.name}}(FloatEnum):
##   -
##   else :
class {{e.name}}(Enum):
##   -
##
##   if len(e.constants) == 0:
  pass
##   -
##   for c in e.constants:
  {{c.name}} = {{hex(c.computed) if c.kind == _p.Constant.INT else repr(c.computed)}}
##   -
##   for c in e.constants:
{{c.name}} = {{e.name}}.{{c.name}}
##   -


## -

## for c in _p.proto.GC:
{{c.name}} = {{hex(c.computed) if c.kind == _p.Constant.INT else repr(c.computed)}}
## -


    


