import os
import hashlib
from uuid import uuid4

from django.db.models import Q
from django.conf import settings


def random_filename(directory, ext=None, root=settings.MEDIA_ROOT):
    """Gets a random untaken filename based on a root, a subdirectory path,
    returns the full path, the filename, and the subdirectory + filename.
    """
    path = ''
    if not os.path.exists(root + directory):
        os.mkdir(root + directory)
    while path == '' or os.path.exists(path):
        filename = hashlib.sha1(str(uuid4())).hexdigest()
        if ext:
            filename += '.' + ext
        path = '%s%s%s' % (
            root,
            directory,
            filename
        )
    return path, filename, directory + filename


def qsearch(qs, search_string):
    qs = qs.filter(
        Q(name__icontains=search_string)
            | Q(reference__icontains=search_string)
            | Q(id__icontains=search_string)
            | Q(description__icontains=search_string)
    )
    return qs
