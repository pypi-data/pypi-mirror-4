import os
import sys
from cement.core import foundation, backend
from cement.core import exc as cement_exc
# from cement.utils import fs

# for some reason, we need this to find modules...?
module_path = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(module_path)

from ntr.cli.controllers.base import NotarioBaseController
from ntr.core import exc as ntr_exc


 # TODO: figure out if we want to have also a ~/notario.ini
file_path = os.path.abspath(__file__)
base_path = os.path.dirname(file_path)
config_path = os.path.join(module_path, 'data/config/notario.cfg')

defaults = backend.defaults('notario')
defaults['notario']['dir'] = "/.notes/"
defaults['notario']['ext'] = ".txt"
defaults['notario']['edt'] = "subl"


class NotarioApp(foundation.CementApp):
    class Meta:
        label = 'notario'
        # bootstrap = 'ntr.cli.bootstrap'
        base_controller = NotarioBaseController

        config_defaults = defaults

        # REVIEW: Should extension be .conf instead?
        config_files = [
            config_path,
            '/etc/notario/notario.cfg',
            '~/.notario.cfg',
            '~/.notario/config'
        ]

    def validate_config(self):
        # fix paths
        def_dir = self.config.get('notario', 'dir')
        abs_dir = os.path.expanduser('~') + def_dir
        self.config.set('notario', 'dir', abs_dir)

        # create abs_path
        if not os.path.exists(abs_dir):
            os.makedirs(abs_dir)


def run():

    app = NotarioApp()
    # app = NotarioApp(config_files=[config_path])

    #handler
    try:
        app.setup()
        # print '--' * 10
        # print app.config.get_sections()
        # print app.config.get('notario', 'debug')
        # print "--" * 10
        app.run()
    except ntr_exc.NotarioArgumentError as e:
        print("NotarioArgumentError: %s" % e.msg)
    except cement_exc.CaughtSignal as e:
        print(e)
    except cement_exc.FrameworkError as e:
        print(e)
    finally:
        app.close()


def get_test_app(**kw):
    from tempfile import mkdtemp

    test_defaults = defaults
    test_defaults['notario']['data_dir'] = mkdtemp()
    kw['defaults'] = kw.get('defaults', defaults)
    kw['config_files'] = kw.get('config_files', [])
    kw['default_sources'] = kw.get('default_sources', None)

    app = NotarioApp(**kw)
    return app

if __name__ == '__main__':
    run()
