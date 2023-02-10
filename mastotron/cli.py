#!/usr/bin/env python3

from .imports import *
from .gui.app import *


@click.command()
@click.option('--gui', is_flag=True, show_default=True, default=False,help='Run embedded in a mini-browser')
@click.option('--bg', is_flag=True, show_default=True, default=False,help='Run in background (use your browser)')
@click.option('--code', is_flag=True, show_default=True, default=False,help='Run in ipython terminal')
def cli(gui=False,bg=False,code=False):
    if code:
        imp='from mastotron import *'
        cmd = ' && '.join([
            f'cd {path_code}',
            f'''ipython -c "{imp}; print('>>> {imp}')" -i'''
        ])
        return os.system(cmd)

    elif bg:
        main()

    else:
        mainview()
    

if __name__=='__main__': cli()