
from repoze.who.plugins.metadata_cache.memory import \
        make_plugin, MetadataCachePluginIdentityMemory

def test_type():
    assert isinstance(make_plugin(), MetadataCachePluginIdentityMemory)

def test_basic_settings():
    plugin = make_plugin(name='userdata', cache='dummy')
    assert plugin.name == 'userdata'
    assert plugin.cache == 'dummy'

def test_plugin_cache():
    """Check that the user's data gets cached for subsequent requests."""
    plugin = make_plugin()

    #Typically more complicated than this, but for testing this is fine
    environ = None
    identity = {'repoze.who.userid': 'david',
                'attributes': {'key': 'value'}}
    plugin.add_metadata(environ, identity)

    #Check that the user's data was cached
    assert 'david' in plugin.cache
    assert {'key': 'value'} == plugin.cache.get('david')
    assert 'attributes' in identity

    #Check that a later request gets the data addeded
    identity2 = {'repoze.who.userid': 'david'}
    plugin.add_metadata(environ, identity2)
    assert 'attributes' in identity2
    assert {'key': 'value'} == identity2.get('attributes')

def test_plugin_noattributes():
    """Check that an unknown user get only a placeholder container.
    """
    plugin = make_plugin()

    environ = None
    identity = {'repoze.who.userid': 'david'}
    plugin.add_metadata(environ, identity)

    assert 'attributes' in identity
    assert identity['attributes'] == {}


