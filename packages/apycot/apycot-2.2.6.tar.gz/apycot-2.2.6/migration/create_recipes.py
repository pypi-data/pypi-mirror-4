from cubes.apycot import recipes

rql('DELETE Recipe R', ask_confirm=False)

for recipe in dir(recipes):
    if recipe.startswith('create_'):
        print recipe
        getattr(recipes, recipe)(session)

# define new recipes for current test config
rql('SET X use_recipe Y WHERE X name "quick", Y name "apycot.recipe.quick"')
rql('SET X use_recipe Y WHERE X name "full", Y name "apycot.recipe.full"')

commit()
