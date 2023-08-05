## Script (Python) "get_plonearticle_ftests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selenium = context.portal_selenium
suite = selenium.getSuite()
target_language = 'en'
suite.setTargetLanguage(target_language)

selenium.addUser(id='sampleadmin', fullname='Sample Admin',
                 roles=['Member', 'Manager'])
selenium.addUser(id='samplemember', fullname='Sample Member',
                 roles=['Member'])

# 1
test_logout = suite.TestLogout()
test_admin_login = suite.TestLoginPortlet('sampleadmin')
test_member_login = suite.TestLoginPortlet('samplemember')
test_switch_language = suite.TestSwitchToLanguage()


glossary_fields = []
glossary_fields.append({'id': 'title',
                        'value': 'Test Glossary'})
glossary_fields.append({'id': 'description',
                        'value': 'This is the test glossary'})
glossary = {'type': 'PloneGlossary',
            'id': 'testglossary',
            'fields': glossary_fields}

glossary_definition_fields = []
glossary_definition_fields.append(
    {'id': 'title',
      'value': 'Test Glossary Definition'})
glossary_definition_fields.append(
    {'id': 'variants',
      'value': 'The test glossary definition variants'})
glossary_definition_fields.append(
    {'id': 'definition',
      'value': 'The test glossary definition text'})
glossary_definition = {
    'type': 'PloneGlossaryDefinition',
    'id': 'testglossarydefinition',
    'fields': glossary_definition_fields,
    }


def test_add_glossary(folder, info):
    return suite.test_add_content(folder, info)


def test_add_glossary_definition(folder, info):
    return suite.test_add_content(folder, info)

suite.addTests("PloneGlossary",
          'Login as Sample Member',
          test_logout,
          test_member_login,
          test_switch_language,
          'Add Glossary',
          test_add_glossary('/Members/samplemember', glossary),
          'Add Glossary Definition',
          test_add_glossary_definition(
              '/Members/samplemember/%s' % glossary['id'],
              glossary_definition),
         )

return suite
