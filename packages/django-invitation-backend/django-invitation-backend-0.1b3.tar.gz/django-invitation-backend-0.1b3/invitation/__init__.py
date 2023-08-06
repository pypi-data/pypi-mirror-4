VERSION = (0, 1, 0, 'beta', 3)

__author__ = u'Daniel Barreto'
__credits__ = [u'Atamert \xd6l\xe7gen']


__license__ = 'BSD'
__maintainer__ = u'Daniel Barreto'
__email__ = 'daniel.barreto.n@gmail.com'
__status__ = 'Beta'

def get_version():
    from django.utils.version import get_version as django_get_version
    return django_get_version(VERSION) # pragma: no cover
