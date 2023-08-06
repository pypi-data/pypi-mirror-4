# schema changes ###############################################################

rename_entity_type('ApycotConfigGroup', 'TestConfigGroup')
rename_entity_type('ProjectApycotConfig', 'TestConfig')
rename_entity_type('ApycotExecution', 'TestExecution')
rename_attribute('TestConfig', 'vcs_tag', 'vcs_branch')
rename_attribute('TestConfigGroup', 'vcs_tag', 'vcs_branch')
add_relation_type('local_repository')
add_relation_type('using_revision')
add_relation_type('test_needs_checkout')
add_relation_type('quick_checks')

add_cube('vcsfile')

# renamed preprocessors and checkers ###########################################

CHK_PP_MAP = {'debian_lint': 'lintian',
              'debian_deb_lint': 'lintian_deb',
              'debian_piuparts': 'piuparts',
              'debian_dpkgdeb': 'dpkg-deb',
              'python_unittest':  'pyunit',
              'python_pytest': 'py.test',
              'python_lint':  'pylint',
              'python_test_coverage': 'pycoverage',
              'python_check': 'pychecker',
              'set_python_env': 'python_setenv',
              'setup_install': 'python_setup',
              }
def update_field(string):
    if string is None:
        return string
    for old, new in CHK_PP_MAP.items():
        string = string.replace(old, new)
    return string

for testconfig in rql('Any X,XC,XCP WHERE X checks XC, X check_preprocessors XCP').entities():
    checks = testconfig.checks
    newchecks = update_field(checks)
    cpp = testconfig.check_preprocessors
    newcpp = update_field(cpp)
    if newchecks != checks or newcpp != cpp:
        testconfig.set_attributes(checks=newchecks, check_preprocessors=newcpp)
checkpoint()

# new expectation for vcs_branch / vcs_path ####################################

rql('SET X vcs_branch NULL WHERE X vcs_repository_type "svn", X vcs_branch "HEAD"')
rql('SET X vcs_path NULL WHERE X vcs_path P, X vcs_repository ~= "%/"+P')
rql('SET X quick_checks "pyunit" WHERE X checks ~= "%pyunit%"')
checkpoint()
