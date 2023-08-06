rql('SET X target "apycot.pylint" WHERE X is RecipeStep, X target "apycot.python.pylint"',
    ask_confirm=True)
commit()

if 'nosy_list' in schema and ('TestConfig', 'CWUser') in schema['nosy_list'].rdefs:
    rql('SET U interested_in PE WHERE TC use_environment PE, '
        'U interested_in TC, NOT U interested_in PE',
        ask_confirm=True)
    drop_relation_definition('CWUser', 'interested_in', 'TestConfig')
    drop_relation_definition('TestConfig', 'nosy_list', 'CWUser')
