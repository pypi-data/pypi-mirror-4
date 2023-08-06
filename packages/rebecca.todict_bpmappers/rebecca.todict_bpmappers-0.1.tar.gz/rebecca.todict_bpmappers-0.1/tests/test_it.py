import pytest
from pyramid import testing

@pytest.fixture
def config(request):
    from rebecca.todict_bpmappers import includeme
    config = testing.setUp()
    config.include(includeme)
    def fin():
        testing.tearDown()
    request.addfinalizer(fin)
    return config


def test_it(config):
    from rebecca.todict import todict
    import dummy
    import venusian

    config.scan(dummy)

    request = testing.DummyRequest()
    person = dummy.Person(name='a', value=100)

    result = todict(request, person)
    
    assert result == dict(username='a', num=100)
