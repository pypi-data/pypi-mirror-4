from optparse import make_option
from django.core.management import BaseCommand
import os
from gametex.models import GameTeXObject, GameTeXField, GameTeXFieldValue, GameTeXClass, GameTeXUser
from gametex.loader import import_gametex, create_users

class Command(BaseCommand):
    """
    Management command for GameTeX loader.
    """
    args = '<path to JSON file> [--clear] [--create-users]'
    help = 'Load data from a GameTeX JSON file.  Updates data in-place unless --clear is passed.'
    option_list = BaseCommand.option_list + (
        make_option('--clear',
                    action='store_true',
                    dest='clear',
                    default=False,
                    help='Delete existing GameTeX objects first.'),
        make_option('--preserve',
                    action='store_true',
                    dest='preserve',
                    default=False,
                    help='If GameTeX data conflicts with database data, preserve the database.'),
        make_option('--create-users',
                    action='store_true',
                    dest='create-users',
                    default=False,
                    help='Create Django users and GameTeXUser models for all PCs.'),
        make_option('--force-create',
                    action='store_true',
                    dest='force-create',
                    default=False,
                    help='Create all valid users even if invalid entries exist.'),
        )

    def handle(self, *args, **options):
        """
        Handler for management command.
        """
        if options['clear']:
            GameTeXFieldValue.objects.all().delete()
            GameTeXField.objects.all().delete()
            GameTeXObject.objects.all().delete()
            GameTeXClass.objects.all().delete()
            GameTeXUser.objects.all().delete()
        if len(args) != 1:
            print 'You must provide the name of a JSON file.'
            return
        if not os.path.exists(args[0]):
            print 'That file doesn\'t exist!'
            return

        import_gametex(args[0], preserve=options['preserve'])
        if options['create-users']:
            create_users(force=options['force-create'])
        print "Done! %s fully loaded." % args[0]
