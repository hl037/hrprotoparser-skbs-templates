"""
hrpotoparser {{_p.name}} plugin.
"""

try:
  inside_skbs_plugin
except:
  from skbs.pluginutils import IsNotAModuleOrScriptError
  raise IsNotAModuleOrScriptError

conf = C(
  #   Predefined template syntax are Tempiny.PY, Tempiny.C and Tempiny.TEX :
  #   Tempiny.C  = dict(stmt_line_start=r'//#', begin_expr='{{be}}', end_expr='{{ee}})
  #   Tempiny.PY = dict(stmt_line_start=r'##', begin_expr='{{be}}', end_expr='{{ee}}')
  #   Tempiny.TEX = dict(stmt_line_start=r'%#', begin_expr='<<', end_expr='>>')
  # tempiny = [
  #   ('*' : Tempiny.PY)
  # ],
  opt_prefix = '_opt.',
  force_prefix = '_force.',
  raw_prefix = '_raw.',
  template_prefix = '_template.',
  #   pathmod_filename = '__pathmod',
)
conf.dir_template_filename = conf.template_prefix

from hrprotoparser.cli import hrprotoparser_cmd

plugin = C()

# Put above additionnal options / arguments
@hrprotoparser_cmd()
def hrpp_cli(proto, **kwargs):
  """
  hrpotoparser {{_p.name}} plugin.
  """
  plugin.update(kwargs)


invokeCmd(hrpp_cli, args)

