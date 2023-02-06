# make sure to use eventlet and call eventlet.monkey_patch()
import eventlet
eventlet.patcher.monkey_patch(select=True, socket=True)

from mastotron.imports import *
import click

#!/usr/bin/env python3

@click.command()
@click.option('-w','--web', is_flag=True, show_default=True, default=False,help='Run as local web server')
@click.option('-c','--code', is_flag=True, show_default=True, default=False,help='Run in ipython terminal')
def cli(web=False,code=False):
    if code:
        imp='from mastotron import *'
        cmd = ' && '.join([
            f'cd {path_code}',
            f'''ipython -c "{imp}; print('>>> {imp}')" -i'''
        ])
        return os.system(cmd)

    from mastotron.gui import app
    return app.mainview()
    


if __name__=='__main__': cli()