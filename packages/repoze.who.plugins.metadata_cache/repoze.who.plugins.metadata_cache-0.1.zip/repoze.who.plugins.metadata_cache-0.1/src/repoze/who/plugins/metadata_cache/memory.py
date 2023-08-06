from zope.interface import implements
from repoze.who.interfaces import IMetadataProvider
from repoze.who.plugins.metadata_cache.base import (MetadataCachePluginBase,
                                                    IMetadataCache)


class MetadataCachePluginIdentityMemory(MetadataCachePluginBase):
    """ A very basic metadata cache plugin that uses a basic dict as cache.

    This is using a (very basic) Python dictionary in memory to
    store metadata, so it won't persist beyond a single Python instance
    and a single process.

    This plugin pulls attributes to cache from the ``repoze.who`` identity
    at some point (eg during initial authentication) and then replays
    them into the identity for subsequent requests.
    """
    implements(IMetadataCache)

    def __init__(self, name='attributes', cache=None):
        """Initialise the metadata cache plugin.

        Arguments/Keywords

        See :meth:`MetadataCachePluginBase.__init__` for basic configuration
        in addition to the following:

        name
           The identifier used to load attributes from within the
           ``repoze.who``identity, and the identifier used to replay
           cached attributes.  This ensures that the downstream application
           will always recieve attributes in the same fashion.

           Default: ``'attributes'``
        cache
           A dict-like structure that will be used to store metadata.
           Replace this with something dict-like if you'd like to use
           another type for storage.

           Default: ``{}`` (empty dict)
        """
        super(MetadataCachePluginIdentityMemory, self).__init__(name=name)
        self.cache = cache or {}

    def get_attributes(self, environ, identity):
        return identity.get(self.name)

    def store(self, key, value):
        self.cache[key] = value

    def fetch(self, key):
        return self.cache.get(key, {})


def make_plugin(name='attributes', cache=None):
    """ Create and configure a :class:`MetadataCacheIdentityMemoryPlugin`.

    See :class:`MetadataCacheIdentityMemoryPlugin` for argument and keyword
    information.
    """
    return MetadataCachePluginIdentityMemory(name=name, cache=cache)


