# postcreate script. You could setup a workflow here for example

wf = add_workflow(u'Test configuration workflow', 'TestConfig')
activated = wf.add_state(_('activated'), initial=True)
deactivated = wf.add_state(_('deactivated'))
wf.add_transition(_('deactivate'), activated, deactivated,
                  requiredgroups=('managers',))
wf.add_transition(_('activate'), deactivated, activated,
                  requiredgroups=('managers',))

from cubes.apycot import recipes
recipes.create_quick_recipe(session)

if not config['pyro-server']:
    config.global_set_option('pyro-server', True)
    config.save()

