def create_quick_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.quick')
    init = recipe.add_step(u'action', u'apycot.init', initial=True)
    getdeps = init.add_next_step(u'action', u'apycot.get_dependencies')
    checkout = getdeps.add_next_step(u'action', u'apycot.checkout', for_each=u'projectenv')
    install = checkout.add_next_step(u'action', u'apycot.install', for_each=u'projectenv')
    pyunit = install.add_next_step(u'action', u'apycot.pyunit', final=True)

def create_full_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.full')
    init = recipe.add_step(u'action', u'apycot.init', initial=True)
    getdeps = init.add_next_step(u'action', u'apycot.get_dependencies')
    checkout = getdeps.add_next_step(u'action', u'apycot.checkout', for_each=u'projectenv')
    install = checkout.add_next_step(u'action', u'apycot.install', for_each=u'projectenv')
    pylint = recipe.add_step(u'action', u'apycot.pylint')
    pyunit = recipe.add_step(u'action', u'apycot.pyunit',
                             arguments=u'EnsureOptions(pycoverage=True)')
    recipe.add_transition(install, (pylint, pyunit))
    pycoverage = pyunit.add_next_step(u'action', u'apycot.pycoverage')
    recipe.add_transition((pylint, pycoverage),
                          recipe.add_step(u'action', u'basic.noop', final=True))
    return recipe
