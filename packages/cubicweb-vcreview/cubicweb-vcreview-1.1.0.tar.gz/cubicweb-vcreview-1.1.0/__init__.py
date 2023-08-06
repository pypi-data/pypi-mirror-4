"""cubicweb-vcreview application package

patch review system on top of vcsfile
"""

import re

EMAIL_RE = re.compile('<([^>]*@[^>]*)>')
def users_by_author(execute, author):
    """Find CWUser related to a patch

    We use revision author email to search for related CWUser."""
    match = EMAIL_RE.search(author)
    if match is not None:
        author_email = match.group(1)
    elif '@' in author:
        author_email = author
    else:
        return []
    rset = execute('DISTINCT Any X WHERE X is CWUser, X use_email E, '
                            'E address ILIKE %(email)s', {'email': author_email})
    return [ueid for ueid, in rset]

def _prepare_patch(patch):
    """Drop all information but the username and patch"""
    cleanpatch = []
    for line in patch.splitlines():
        if line.startswith('# User') or not line.startswith('#'):
            if line.startswith('@@'):
                line = '@@\n'
            cleanpatch.append(line)
    return cleanpatch


def compare_patches(old, new):
    """Compare two patches in git format."""
    return _prepare_patch(old) == _prepare_patch(new)
