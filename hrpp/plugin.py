"""
skbs plugin to bootstrap hrpotoparser plugin !
"""

try:
  inside_skbs_plugin
except:
  from skbs.pluginutils import IsNotAModuleOrScriptError
  raise IsNotAModuleOrScriptError

conf = C(
  #   Predefined template syntax are Tempiny.PY, Tempiny.C and Tempiny.TEX :
  #   Tempiny.C  = dict(stmt_line_start=r'//#', begin_expr=', end_expr=')
  #   Tempiny.PY = dict(stmt_line_start=r'##', begin_expr=', end_expr=')
  #   Tempiny.TEX = dict(stmt_line_start=r'%#', begin_expr='<<', end_expr='>>')
  # tempiny = [
  #   ('*' : Tempiny.PY)
  # ],
  opt_prefix = '_opt.',
  force_prefix = '_force.',
  raw_prefix = None,
  template_prefix = '_template.',
  #   pathmod_filename = '__pathmod',
)
conf.dir_template_filename = conf.template_prefix

plugin = C()

import click

@click.command()
@click.option('--name', '-n', type=str, prompt=True)
def cli(**kwargs):
  plugin.update(kwargs)

invokeCmd(cli, args)

