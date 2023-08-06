from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.utils.importlib import import_module
import chameleon, os


class Command(TemplateCommand):
    help = ("Creates a pluggable django theme directory structure for the specified "
            "theme name in the current project.")

    def handle(self, app_name=None, target=None, **options):
        if app_name is None:
            raise CommandError("you must provide a theme name")

        options['template'] = options.get('template') or os.path.join(chameleon.__path__[0], 'conf', 'app_template')

        ###TODO: need to find a way to make this part work.  Unfortunately, HTML templates already ARE templates
        #options['extensions'] += ['html','md', 'less', 'css',]
        options['extensions'] += ['less', 'css',]

        # Check that the app_name cannot be imported.
        try:
            import_module(app_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing "
                               "Python module and cannot be used as a theme "
                               "name. Please try another name." % app_name)

        super(Command, self).handle('app', app_name, target, **options)

