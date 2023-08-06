# About

Dispose of media files that are no longer referenced in the database.

# Setup

Install with pip:

    pip install git+https://bitbucket.org/danhawkes/django-dispose.git#egg=django-dispose

Add to the installed apps in `settings.py`

    INSTALLED_APPS = (
    	...
        'django_dispose'
    )

Add definitions for apps and directories to search:

    DISPOSE_MEDIA = {
    	# name of app
        'app1': {
        	# root directory of media files in this app
            'root': path.join(MEDIA_ROOT, 'app1'),
            # list of subdirectories to ignore
            'skip': [path.join(MEDIA_ROOT, 'app1', 'subdir1'),
                     path.join(MEDIA_ROOT, 'app1', 'subdir2')]
        },
        # another app
        'app2': {
            'root': path.join(MEDIA_ROOT, 'app2')
        },
    }

# Run

List files and prompt for confirmation before deleting:

    python manage.py dispose

Alternatively, delete without prompting:

    python manage.py dispose --noinput

# License

MIT - See LICENSE file.
