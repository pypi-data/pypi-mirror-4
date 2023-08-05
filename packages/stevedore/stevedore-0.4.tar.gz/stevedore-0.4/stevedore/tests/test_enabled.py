from stevedore import enabled


def test_enabled():
    def check_enabled(ep):
        return ep.name == 't2'
    em = enabled.EnabledExtensionManager(
        'stevedore.test.extension',
        check_enabled,
        invoke_on_load=True,
        invoke_args=('a',),
        invoke_kwds={'b': 'B'},
        )
    assert len(em.extensions) == 1
    assert em.names() == ['t2']
