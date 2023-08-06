rql('DELETE CheckResultLog X')
checkpoint()
drop_attribute('CheckResultLog', 'severity')
add_attribute('CheckResultLog', 'severity')

sql('''CREATE FUNCTION severity_sort_value(text) RETURNS int
    AS 'return {"DEBUG": 0, "INFO": 10, "WARNING": 20, "ERROR": 30, "FATAL": 40}[args[0]]'
    LANGUAGE plpythonu;
''')
checkpoint()

synchronize_eschema('CheckResultLog')
synchronize_eschema('CheckResult')
