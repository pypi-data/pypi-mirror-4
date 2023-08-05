__author__ = 'ternus'

from models import *
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
        g = GTO.objects.get_or_create(macro=obj['macro'])
        if not g[1]:
            print "<found!> ",
        g = g[0]
        if not (g.name and preserve):
            g.name = obj['name']
        g.save()
        print '[',
        for cls in obj['classes']:
            c = GameTeXClass.objects.get_or_create(name=cls)[0]
            g.classes.add(c)
            print cls,
        print '] { ',
        for field in obj:
            if field == 'macro' or field == 'name' or field == 'classes': continue
            f = GameTeXField.objects.get_or_create(name=field)[0]
            v = GameTeXFieldValue.objects.get_or_create(field=f, object=g)
            if v[1] or not preserve:
                v[0].value=obj[field]
                print "%s=%s " % (field, obj[field]),
            else:
                print "%s==%s " % (field, v[0].value),
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
    for pc in pcs:
        if not pc.has_field('username'):
            print "PC %s (%s) doesn't have username set!" % (pc.name, pc.macro)
            fail = True
        if not pc.has_field('password'):
            print "PC %s (%s) doesn't have password set!" % (pc.name, pc.macro)
            fail = True
    if fail and not force:
        print "Couldn't import -- fix errors first."
        return False
    for pc in pcs:
        if not (pc.has_field('username') and pc.has_field('password')): continue
        u = User.objects.create_user(username=pc.username, password=pc.password)
        GameTeXUser.objects.get_or_create(gto=pc,user=u)
        print "Created %s" % pc.username
    print "Done creating users."
