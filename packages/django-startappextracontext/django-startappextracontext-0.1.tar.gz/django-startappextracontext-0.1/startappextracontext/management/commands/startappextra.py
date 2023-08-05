from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.utils.importlib import import_module

from optparse import Option

# http://djangosnippets.org/snippets/1617/
class DictOption(Option):
    """
    A parseopt option that let's me define a dictionary through
    the commandline.
    
    optparse example:
    parser.add_option(DictOption("-p","--passwords",dest="passwords",type="string",action="dic"))
    
    Commandline usage:
    --passwords=[localhost]value,[slicehost]whatever
    
    Commandline, if spaces are needed:
    --passwords="[localhost]my Password,[slicehost]Anot erPassword"
    
    This would be defined in the final options dictionary as another dictionary:
    example 1: { 'passwords':{'localhost':'value' } }
    example 2: { 'passwords':{'localhost':'my Password', 'slicehost':'Anot erPassword' } }
    """
    ACTIONS = Option.ACTIONS + ("dic",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("dic",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("dic",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("dic",)
    def take_action(self,action,dest,opt,value,values,parser):
        if action=="dic":
            vals=value.split(",")
            d={}
            for val in vals:
                p=val.split("]")
                k=p[0][1:]
                v=p[1]
                d[k]=v
            setattr(values,dest,d)
        else: Option.take_action(self, action, dest, opt, value, values, parser)

class Command(TemplateCommand):
    help = ("Creates a Django app directory structure for the given app "
            "name in the current directory or optionally in the given "
            "directory. Additionally takes extra context and passes it to"
            "the app template.")


    option_list = TemplateCommand.option_list + (
        DictOption('--extra-context',
                    dest='extra_context', help='Extra context in dictionary form. Example:'
                    ' --extra-context=[key]value,[key2]value2'
                    'Use double quotes around argument if spaces are needed.', 
                    type='string', action='dic'),
        )

    def handle(self, app_name=None, target=None, **options):

        extra_context = options.pop('extra_context', None)
        if extra_context != None:
            options.update(extra_context)

        super(Command, self).handle('app', app_name, target, **options)
