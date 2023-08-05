# coding=utf-8
"""
GameTeX models.
"""

__author__ = 'ternus'


from gametex.models import GameTeXClass, GameTeXField, \
			   GameTeXFieldValue, GameTeXUser, GTO
import json

def import_gametex(filename, preserve=False):
    """
    Import GameTeX from a file.  Assumes file exists and is sane JSON.

    If preserve is True, when merging with existing content, prioritize
    the database's value over the JSON file's.
    """
    print "Importing GameTeX from %s." % filename
    if preserve:
        print "Preserving existing database values."
    gametex_file = file(filename, 'r')
    gametex_json = json.load(gametex_file)
    print "Found %d objects." % len(gametex_json)
    for obj in gametex_json:
        print "Loading %s... " % (obj['macro'] if 'macro' in obj else ''),
        gto = GTO.objects.get_or_create(macro = obj['macro'])
        if not gto[1]:
            print "<found!> ",
        gto = gto[0]
        if not (gto.name and preserve):
            gto.name = obj['name']
        gto.save()
        print '[',
        for cls in obj['classes']:
            clx = GameTeXClass.objects.get_or_create(name = cls)[0]
            gto.classes.add(clx)
            print cls,
        print '] { ',
        for field in obj:
            if field == 'macro' or field == 'name' or field == 'classes':
                continue
            fld = GameTeXField.objects.get_or_create(name = field)[0]
            val = GameTeXFieldValue.objects.get_or_create(field = fld,
                                                          object = gto)
            if val[1] or not preserve:
                val[0].value = obj[field]
                print "%s=%s " % (field, obj[field]),
            else:
                print "%s==%s " % (field, val[0].value),
        print "} done."
    print "Done loading GameTeX objects."

def create_users(force=False):
    """
    Automatically create users from GameTeX objects.
    
    If force is True, ignore errors.
    """
    print "Creating users..."
    from django.contrib.auth.models import User
    pcs = GTO.bc('PC')

    # sanity check
    fail = False
    for char in pcs:
        if not char.has_field('username'):
            print "PC %s (%s) doesn't have username set!" % (char.name,
                                                             char.macro)
            fail = True
        if not char.has_field('password'):
            print "PC %s (%s) doesn't have password set!" % (char.name,
                                                             char.macro)
            fail = True
    if fail and not force:
        print "Couldn't import -- fix errors first."
        return False
    for char in pcs:
        if not (char.has_field('username') and char.has_field('password')):
            continue
        usr = User.objects.create_user(username=char.username,
                                     password=char.password)
        GameTeXUser.objects.get_or_create(gto=char, user=usr)
        print "Created %s" % char.username
    print "Done creating users."
