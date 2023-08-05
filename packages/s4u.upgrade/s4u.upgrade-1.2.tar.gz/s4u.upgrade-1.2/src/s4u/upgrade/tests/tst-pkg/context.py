from s4u.upgrade import upgrade_context


@upgrade_context('foo')
def step(environment):  # pragma: no cover
    pass
