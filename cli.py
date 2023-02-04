from mastotron.imports import *
import click

#!/usr/bin/env python3

@click.command()
@click.option('-g','--gui', is_flag=True, show_default=True, default=False,help='Run as electron app (default)')
@click.option('-w','--web', is_flag=True, show_default=True, default=False,help='Run as local web server')
@click.option('-c','--code', is_flag=True, show_default=True, default=False,help='Run in ipython terminal')
def cli(gui=False,web=False,code=False):
    if web:
        return os.system(f'cd {path_web} && python app.py')

    if code:
        imp='from mastotron import *'
        cmd = ' && '.join([
            f'cd {path_code}',
            f'''ipython -c "{imp}; print('>>> {imp}')" -i'''
        ])
        return os.system(cmd)

    #if gui:
    return os.system(f'cd {path_gui} && npm start')
    


if __name__=='__main__': cli()