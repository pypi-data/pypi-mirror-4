import logging

from repoze.who.interfaces import IMetadataProvider
from zope.interface import implements, Interface


log = logging.getLogger(__name__)


class IMetadataCache(Interface):
    """ Interface for metadata caches.
    """

    def get_attributes(self, environ, identity):
        """ Return a value representing metadata able to be stored in the cache.

        This method can use either the ``environ``, ``identity`` or both
        to build a set of suitable attributes.
        """

    def store(self, key, value):
        """ Store the given ``value`` into a cache using the given ``key``.
        """

    def fetch(self, key):
        """ Fetch the given value associated with the ``key`` from the cache.
        """


class MetadataCachePluginBase(object):
    """ ``repoze.who`` plugin to cache identity metadata for later use.

    This plugin stores some data in the identity - referenced by
    :attr:`MetdataCachePlugin.name` - into a cache for recall on
    subsequent requests. Useful in the situation where another plugin
    has obtained a user's metadata during its non-``add_metadata`` process
    and needs to store it somewhere for later recall.

    A prime example of this is CAS authentication and attribute
    release.  The CAS plugin from ``repoze.who.plugins.cas`` is a
    ``repoze.who`` ``identifier`` and user metadata attributes are
    released from the CAS server during this identification process.
    So, when the CAS service ticket is validated against the server,
    metdata is returned part of the same response. As there is no
    way to directly save this information during the identification
    process, that plugin simply returns the metadata as part of the
    identity.  Then, this plugin can capture the metadata out of the
    identity and store it for later use.

    This class is designed to be extended or modified by any future
    ``cache`` types. Create your own class as a proxy if you'd like to easily
    use some other storage method.

    Note: This is a work in progress.
    """
    implements(IMetadataProvider)

    def __init__(self, name='attributes'):
        """Initialise the metadata cache plugin.

        Arguments/Keywords

        name
           Identifier within the ``repoze.who`` identity to locate
           incoming data to cache.  The same identifier will be where
           cached metadata is restored to on later requests.

           Default: ``'attributes'``
        """
        self.name = name

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        """ Add user metadata into the identity, or cache if present.
        """
        userid = identity.get('repoze.who.userid')
        if userid:
            attributes = self.get_attributes(environ, identity)
            if attributes:
                log.debug("Storing incoming attributes to cache.")
                self.store(userid, attributes)
            else:
                log.debug("Fetching attributes from cache into identity.")
                identity[self.name] = self.fetch(userid)


