#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django_dispose.app_settings import DISPOSE_MEDIA
from itertools import chain
from optparse import make_option
import os
import shutil
from django.conf import settings


def ask_user():
    answer = raw_input('\tContinue? [y|n]\n\t')
    return (answer in ['y', 'Y', 'yes', 'YES'])


def get_total_size_mb(files):
    total = 0
    for f in files:
        total += os.path.getsize(f)
    return (total / (1024 * 1024.0))


def print_info(app_name, delete_files, empty_dirs):
    if delete_files:
        print "\n\tFiles to be deleted:"
        print '\t', ("\n\t").join(delete_files)
    if empty_dirs:
        print "\n\tEmpty directories to be removed:"
        print '\t', ("\n\t").join(empty_dirs)

    if delete_files or empty_dirs:
        num_items = len(delete_files) + len(empty_dirs)
        total_to_free = ("%0.2f MB" % get_total_size_mb(delete_files))
        print "\n\tIn total, %s in %s items will be deleted.\n" \
        % (total_to_free, num_items)
    else:
        print "\n\tNo disposable files were found.\n"


def get_needed_files(app):
    needed_files = []
    for model in ContentType.objects.filter(app_label=app):
        mc = model.model_class()
        if mc:

            # build list of model field names that are filefields
            fields = []
            for field in mc._meta.fields:
                if field.get_internal_type() == 'FileField':
                    fields.append(field.name)

            # build list of referenced filenames
            if fields:
                filenames = mc.objects.all().values_list(*fields)
                needed_files.extend([os.path.join(settings.MEDIA_ROOT, fn) \
                                     for fn in chain.from_iterable(filenames)])

    return needed_files


def get_deletables(rootdir, skip_dirs, needed_files):

    all_files = []
    empty_dirs = []

    for dirpath, dirnames, filenames in os.walk(rootdir):

        # top-down iterating: remove directories that are in 'skip'
        for dirname in dirnames:
            if os.path.join(dirpath, dirname) in skip_dirs:
                dirnames.remove(dirname)

        # collect files
        all_files.extend([os.path.join(dirpath, fn) for fn in filenames])

        # collect empty directories
        if not filenames and not dirnames:
            empty_dirs.append(dirpath)

    delete_files = list(set(all_files).difference(needed_files))
    delete_files.sort()
    empty_dirs.sort()

    return delete_files, empty_dirs


def do_delete(delete_files, empty_dirs):
    for f in delete_files:
        # only delete if file still exists
        if os.path.isfile(f):
            os.remove(f)
    for d in empty_dirs:
        shutil.rmtree(d, ignore_errors=True)


class Command(BaseCommand):

    help = "Disposes of media files that are not referenced in the database."
    base_options = (make_option('--noinput', action='store_true',
                                dest='noinput', default=False,
                                help='Delete files without prompting for \
                                confirmation.'),)
    option_list = BaseCommand.option_list + base_options

    def handle(self, **options):
        self.noinput = options.get('noinput')
        delete_files = []
        empty_dirs = []

        for app in DISPOSE_MEDIA:

            root_dir = DISPOSE_MEDIA[app]['root']
            skip_dirs = DISPOSE_MEDIA[app].get('skip', ())

            needed_files = get_needed_files(app)
            files, dirs = get_deletables(root_dir, skip_dirs, needed_files)
            delete_files.extend(files)
            empty_dirs.extend(dirs)

        print_info(app, delete_files, empty_dirs)

        if delete_files or empty_dirs:
            if self.noinput or ask_user():
                do_delete(delete_files, empty_dirs)
