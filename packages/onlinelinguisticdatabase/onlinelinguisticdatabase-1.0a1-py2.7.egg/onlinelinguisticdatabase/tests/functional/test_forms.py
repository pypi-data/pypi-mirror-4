# Copyright 2013 Joel Dunham
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime
import logging
import os
from time import sleep
import simplejson as json
from nose.tools import nottest
from base64 import encodestring
from paste.deploy import appconfig
from sqlalchemy.sql import desc
from uuid import uuid4
from onlinelinguisticdatabase.lib.SQLAQueryBuilder import SQLAQueryBuilder
from onlinelinguisticdatabase.tests import *
import onlinelinguisticdatabase.model as model
from onlinelinguisticdatabase.model.meta import Session
import onlinelinguisticdatabase.lib.helpers as h
import webtest

log = logging.getLogger(__name__)


def addSEARCHToWebTestValidMethods():
    new_valid_methods = list(webtest.lint.valid_methods)
    new_valid_methods.append('SEARCH')
    new_valid_methods = tuple(new_valid_methods)
    webtest.lint.valid_methods = new_valid_methods


class TestFormsController(TestController):

    here = appconfig('config:test.ini', relative_to='.')['here']
    filesPath = os.path.join(here, 'files')
    testFilesPath = os.path.join(here, 'test_files')
    reducedFilesPath = os.path.join(filesPath, u'reduced_files')

    createParams = {
        'transcription': u'',
        'phoneticTranscription': u'',
        'narrowPhoneticTranscription': u'',
        'morphemeBreak': u'',
        'grammaticality': u'',
        'morphemeGloss': u'',
        'translations': [],
        'comments': u'',
        'speakerComments': u'',
        'elicitationMethod': u'',
        'tags': [],
        'syntacticCategory': u'',
        'speaker': u'',
        'elicitor': u'',
        'verifier': u'',
        'source': u'',
        'status': u'tested',
        'dateElicited': u''     # mm/dd/yyyy
    }

    createFileParams = {
        'name': u'',
        'description': u'',
        'dateElicited': u'',    # mm/dd/yyyy
        'elicitor': u'',
        'speaker': u'',
        'utteranceType': u'',
        'embeddedFileMarkup': u'',
        'embeddedFilePassword': u'',
        'tags': [],
        'forms': [],
        'file': ''      # file data Base64 encoded
    }

    extra_environ_view = {'test.authentication.role': u'viewer'}
    extra_environ_contrib = {'test.authentication.role': u'contributor'}
    extra_environ_admin = {'test.authentication.role': u'administrator'}
    json_headers = {'Content-Type': 'application/json'}

    # Set up some stuff for the tests
    def setUp(self):
        pass

    # Clear all models in the database except Language; recreate the users.
    def tearDown(self):
        h.clearAllModels()
        administrator = h.generateDefaultAdministrator()
        contributor = h.generateDefaultContributor()
        viewer = h.generateDefaultViewer()
        Session.add_all([administrator, contributor, viewer])
        Session.commit()

        h.clearDirectoryOfFiles(self.filesPath)
        h.clearDirectoryOfFiles(self.reducedFilesPath)

        # Perform a vacuous GET just to delete app_globals.applicationSettings
        # to clean up for subsequent tests.
        extra_environ = self.extra_environ_admin.copy()
        extra_environ['test.applicationSettings'] = True
        response = self.app.get(url('forms'), extra_environ=extra_environ)


    #@nottest
    def test_index(self):
        """Tests that GET /forms returns a JSON array of forms with expected values."""

        # Test that the restricted tag is working correctly.
        # First get the users.
        users = h.getUsers()
        administratorId = [u for u in users if u.role == u'administrator'][0].id
        contributorId = [u for u in users if u.role == u'contributor'][0].id
        viewerId = [u for u in users if u.role == u'viewer'][0].id

        # Then add a contributor and a restricted tag.
        restrictedTag = h.generateRestrictedTag()
        myContributor = h.generateDefaultUser()
        myContributorFirstName = u'Mycontributor'
        myContributor.firstName = myContributorFirstName
        Session.add_all([restrictedTag, myContributor])
        Session.commit()
        myContributor = Session.query(model.User).filter(
            model.User.firstName == myContributorFirstName).first()
        myContributorId = myContributor.id
        restrictedTag = h.getRestrictedTag()

        # Then add the default application settings with myContributor as the
        # only unrestricted user.
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.unrestrictedUsers = [myContributor]
        Session.add(applicationSettings)
        Session.commit()

        # Finally, issue two POST requests to create two default forms with the
        # *default* contributor as the enterer.  One form will be restricted and
        # the other will not be.
        extra_environ = {'test.authentication.id': contributorId,
                         'test.applicationSettings': True}

        # Create the restricted form.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test restricted tag transcription',
            'translations': [{'transcription': u'test restricted tag translation',
                         'grammaticality': u''}],
            'tags': [h.getTags()[0].id]    # the restricted tag should be the only one
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                        extra_environ)
        resp = json.loads(response.body)
        restrictedFormId = resp['id']

        # Create the unrestricted form.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test restricted tag transcription 2',
            'translations': [{'transcription': u'test restricted tag translation 2',
                         'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                        extra_environ)
        resp = json.loads(response.body)
        unrestrictedFormId = resp['id']

        # Expectation: the administrator, the default contributor (qua enterer)
        # and the unrestricted myContributor should all be able to view both forms.
        # The viewer will only receive the unrestricted form.

        # An administrator should be able to view both forms.
        extra_environ = {'test.authentication.role': 'administrator',
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 2
        assert resp[0]['transcription'] == u'test restricted tag transcription'
        assert resp[0]['morphemeBreakIDs'] == None
        assert resp[0]['morphemeBreakIDs'] == None
        assert resp[0]['translations'][0]['transcription'] == u'test restricted tag translation'
        assert type(resp[0]['translations'][0]['id']) == type(1)
        assert type(resp[0]['id']) == type(1)
        assert response.content_type == 'application/json'

        # The default contributor (qua enterer) should also be able to view both
        # forms.
        extra_environ = {'test.authentication.id': contributorId,
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 2

        # Mycontributor (an unrestricted user) should also be able to view both
        # forms.
        extra_environ = {'test.authentication.id': myContributorId,
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 2

        # A (not unrestricted) viewer should be able to view only one form.
        extra_environ = {'test.authentication.role': 'viewer',
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 1

        # Remove Mycontributor from the unrestricted users list and access to
        # the second form will be denied.
        applicationSettings = h.getApplicationSettings()
        applicationSettings.unrestrictedUsers = []
        Session.add(applicationSettings)
        Session.commit()

        # Mycontributor (no longer an unrestricted user) should now *not* be
        # able to view the restricted form.
        extra_environ = {'test.authentication.id': myContributorId,
                         'test.applicationSettings': True,
                         'test.retainApplicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 1

        # Remove the restricted tag from the form and the viewer should now be
        # able to view it too.
        restrictedForm = Session.query(model.Form).get(restrictedFormId)
        restrictedForm.tags = []
        Session.add(restrictedForm)
        Session.commit()
        extra_environ = {'test.authentication.role': 'viewer',
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 2

        # Clear all Forms (actually, everything but the tags, users and languages)
        h.clearAllModels(['User', 'Tag', 'Language'])

        # Now add 100 forms.  The even ones will be restricted, the odd ones not.
        def createFormFromIndex(index):
            form = model.Form()
            form.transcription = u'transcription %d' % index
            return form
        forms = [createFormFromIndex(i) for i in range(1, 101)]
        Session.add_all(forms)
        Session.commit()
        forms = h.getForms()
        restrictedTag = h.getRestrictedTag()
        for form in forms:
            if int(form.transcription.split(' ')[1]) % 2 == 0:
                form.tags.append(restrictedTag)
            Session.add(form)
        Session.commit()
        forms = h.getForms()    # ordered by Form.id ascending

        # An administrator should be able to retrieve all of the forms.
        extra_environ = {'test.authentication.role': 'administrator',
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp) == 100
        assert resp[0]['transcription'] == u'transcription 1'
        assert resp[0]['id'] == forms[0].id

        # Test the paginator GET params.
        paginator = {'itemsPerPage': 23, 'page': 3}
        response = self.app.get(url('forms'), paginator, headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp['items']) == 23
        assert resp['items'][0]['transcription'] == forms[46].transcription

        # Test the orderBy GET params.
        orderByParams = {'orderByModel': 'Form', 'orderByAttribute': 'transcription',
                     'orderByDirection': 'desc'}
        response = self.app.get(url('forms'), orderByParams,
                        headers=self.json_headers, extra_environ=extra_environ)
        resp = json.loads(response.body)
        resultSet = sorted([f.transcription for f in forms], reverse=True)
        assert resultSet == [f['transcription'] for f in resp]

        # Test the orderBy *with* paginator.
        params = {'orderByModel': 'Form', 'orderByAttribute': 'transcription',
                     'orderByDirection': 'desc', 'itemsPerPage': 23, 'page': 3}
        response = self.app.get(url('forms'), params,
                        headers=self.json_headers, extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert resultSet[46] == resp['items'][0]['transcription']

        # The default viewer should only be able to see the odd numbered forms,
        # even with a paginator.
        itemsPerPage = 7
        page = 7
        paginator = {'itemsPerPage': itemsPerPage, 'page': page}
        extra_environ = {'test.authentication.role': 'viewer',
                         'test.applicationSettings': True}
        response = self.app.get(url('forms'), paginator, headers=self.json_headers,
                                extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp['items']) == itemsPerPage
        assert resp['items'][0]['transcription'] == u'transcription %d' % (
            ((itemsPerPage * (page - 1)) * 2) + 1)

        # Expect a 400 error when the orderByDirection param is invalid
        orderByParams = {'orderByModel': 'Form', 'orderByAttribute': 'transcription',
                     'orderByDirection': 'descending'}
        response = self.app.get(url('forms'), orderByParams, status=400,
            headers=self.json_headers, extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert resp['errors']['orderByDirection'] == u"Value must be one of: asc; desc (not u'descending')"

        # Expect the default BY id ASCENDING ordering when the orderByModel/Attribute
        # param is invalid.
        orderByParams = {'orderByModel': 'Formosa', 'orderByAttribute': 'transcrumption',
                     'orderByDirection': 'desc'}
        response = self.app.get(url('forms'), orderByParams,
            headers=self.json_headers, extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert resp[0]['id'] == forms[0].id

        # Expect a 400 error when the paginator GET params are, empty, not
        # or integers that are less than 1
        paginator = {'itemsPerPage': u'a', 'page': u''}
        response = self.app.get(url('forms'), paginator, headers=self.json_headers,
                                extra_environ=extra_environ, status=400)
        resp = json.loads(response.body)
        assert resp['errors']['itemsPerPage'] == u'Please enter an integer value'
        assert resp['errors']['page'] == u'Please enter a value'

        paginator = {'itemsPerPage': 0, 'page': -1}
        response = self.app.get(url('forms'), paginator, headers=self.json_headers,
                                extra_environ=extra_environ, status=400)
        resp = json.loads(response.body)
        assert resp['errors']['itemsPerPage'] == u'Please enter a number that is 1 or greater'
        assert resp['errors']['page'] == u'Please enter a number that is 1 or greater'

    #@nottest
    def test_create(self):
        """Tests that POST /forms correctly creates a new form."""

        # Pass some mal-formed JSON to test that a 400 error is returned.
        params = '"a'   # Bad JSON
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        assert resp['error'] == u'JSON decode error: the parameters provided were not valid JSON.'

        # Create a test form.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test_create_transcription',
            'translations': [{'transcription': u'test_create_translation', 'grammaticality': u''}],
            'status': u'tested'
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert type(resp) == type({})
        assert resp['transcription'] == u'test_create_transcription'
        assert resp['translations'][0]['transcription'] == u'test_create_translation'
        assert resp['morphemeBreakIDs'] == None
        assert resp['enterer']['firstName'] == u'Admin'
        assert resp['status'] == u'tested'
        assert formCount == 1
        assert response.content_type == 'application/json'

        # Add an empty application settings and two syntactic categories.
        N = h.generateNSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        S = h.generateSSyntacticCategory()
        Agr = model.SyntacticCategory()
        Agr.name = u'Agr'
        applicationSettings = model.ApplicationSettings()
        Session.add_all([S, N, Num, Agr, applicationSettings])
        Session.commit()
        NId = N.id
        NumId = Num.id
        AgrId = Agr.id

        # Create three lexical forms, two of which are disambiguated only by their
        # category

        # chien/dog/N
        params = self.createParams.copy()
        params.update({
            'transcription': u'chien',
            'morphemeBreak': u'chien',
            'morphemeGloss': u'dog',
            'translations': [{'transcription': u'dog', 'grammaticality': u''}],
            'syntacticCategory': NId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        dogId = resp['id']

        # s/PL/Num
        params = self.createParams.copy()
        params.update({
            'transcription': u's',
            'morphemeBreak': u's',
            'morphemeGloss': u'PL',
            'translations': [{'transcription': u'plural', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        pluralNumId = resp['id']
        formCount = Session.query(model.Form).count()
        assert formCount == 3

        # s/PL/Agr
        params = self.createParams.copy()
        params.update({
            'transcription': u's',
            'morphemeBreak': u's',
            'morphemeGloss': u'PL',
            'translations': [{'transcription': u'plural', 'grammaticality': u''}],
            'syntacticCategory': AgrId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        pluralAgrId = resp['id']

        # Create another form whose morphemic analysis will reference the
        # lexical items created above.  Since the current application settings
        # lists no morpheme delimiters, each word will be treated as a morpheme
        # by compileMorphemicAnalysis.
        params = self.createParams.copy()
        params.update({
            'transcription': u'Les chiens aboient.',
            'morphemeBreak': u'les chien-s aboient',
            'morphemeGloss': u'the dog-PL bark',
            'translations': [{'transcription': u'The dogs are barking.', 'grammaticality': u''}],
            'syntacticCategory': Session.query(
                model.SyntacticCategory).filter(
                model.SyntacticCategory.name==u'S').first().id
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert type(resp) == type({})
        assert resp['transcription'] == u'Les chiens aboient.'
        assert resp['translations'][0]['transcription'] == u'The dogs are barking.'
        assert resp['syntacticCategory']['name'] == u'S'
        assert resp['morphemeBreakIDs'] == [[[]], [[]], [[]]]
        assert resp['morphemeGlossIDs'] == [[[]], [[]], [[]]]
        assert resp['syntacticCategoryString'] == u'? ? ?'
        assert resp['breakGlossCategory'] == u'les|the|? chien-s|dog-PL|? aboient|bark|?'
        assert resp['syntacticCategory']['name'] == u'S'
        assert formCount == 5

        # Re-create the form from above but this time add a non-empty
        # application settings.  Now we should expect the morphemeBreakIDs,
        # morphemeGlossIDs and syntacticCategoryString to have non-vacuous
        # values since '-' is specified as a morpheme delimiter.
        applicationSettings = h.generateDefaultApplicationSettings()
        Session.add(applicationSettings)
        Session.commit()
        response = self.app.post(url('forms'), params, self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert resp['morphemeBreakIDs'][1][0][0][2] == u'N'
        assert formCount == 6
        assert resp['morphemeBreakIDs'][0] == [[]]
        assert resp['morphemeBreakIDs'][1][0][0][0] == dogId
        assert resp['morphemeBreakIDs'][1][0][0][1] == u'dog'
        assert resp['morphemeBreakIDs'][1][0][0][2] == u'N'
        assert resp['morphemeBreakIDs'][1][1][0][0] == pluralNumId
        assert resp['morphemeBreakIDs'][1][1][0][1] == u'PL'
        assert resp['morphemeBreakIDs'][1][1][0][2] == u'Num'
        assert resp['morphemeBreakIDs'][1][1][1][0] == pluralAgrId
        assert resp['morphemeBreakIDs'][1][1][1][1] == u'PL'
        assert resp['morphemeBreakIDs'][1][1][1][2] == u'Agr'
        assert resp['morphemeBreakIDs'][2] == [[]]
        assert resp['morphemeGlossIDs'][0] == [[]]
        assert resp['morphemeGlossIDs'][1][0][0][0] == dogId
        assert resp['morphemeGlossIDs'][1][0][0][1] == u'chien'
        assert resp['morphemeGlossIDs'][1][0][0][2] == u'N'
        assert resp['morphemeGlossIDs'][1][1][0][0] == pluralNumId
        assert resp['morphemeGlossIDs'][1][1][0][1] == u's'
        assert resp['morphemeGlossIDs'][1][1][0][2] == u'Num'
        assert resp['morphemeGlossIDs'][1][1][1][0] == pluralAgrId
        assert resp['morphemeGlossIDs'][1][1][1][1] == u's'
        assert resp['morphemeGlossIDs'][1][1][1][2] == u'Agr'
        assert resp['morphemeGlossIDs'][2] == [[]]
        assert resp['syntacticCategoryString'] == u'? N-Num ?'
        assert resp['breakGlossCategory'] == u'les|the|? chien|dog|N-s|PL|Num aboient|bark|?'

        # Recreate the above form but put morpheme delimiters in unexpected
        # places.
        params = self.createParams.copy()
        params.update({
            'transcription': u'Les chiens aboient.',
            'morphemeBreak': u'les chien- -s aboient',
            'morphemeGloss': u'the dog- -PL bark',
            'translations': [{'transcription': u'The dogs are barking.', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        morphemeBreakIDs = resp['morphemeBreakIDs']
        assert len(morphemeBreakIDs) == 4   # 3 spaces in the mb field
        assert len(morphemeBreakIDs[1]) == 2 # 'chien-' is split into 'chien' and ''
        assert 'N-?' in resp['syntacticCategoryString'] and \
            '?-Num' in resp['syntacticCategoryString']

    #@nottest
    def test_create_invalid(self):
        """Tests that POST /forms with invalid input returns an appropriate error."""

        # Empty transcription and translations should raise error
        formCount = Session.query(model.Form).count()
        params = self.createParams.copy()
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        assert resp['errors']['transcription'] == u'Please enter a value'
        assert resp['errors']['translations'] == u'Please enter a value'
        assert newFormCount == formCount

        # Exceeding length restrictions should return errors also.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test create invalid transcription' * 100,
            'grammaticality': u'*',
            'phoneticTranscription': u'test create invalid phonetic transcription' * 100,
            'narrowPhoneticTranscription': u'test create invalid narrow phonetic transcription' * 100,
            'morphemeBreak': u'test create invalid morpheme break' * 100,
            'morphemeGloss': u'test create invalid morpheme gloss' * 100,
            'translations': [{'transcription': 'test create invalid translation', 'grammaticality': u''}],
            'status': u'invalid status value'
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        tooLongError = u'Enter a value not more than 255 characters long'
        assert resp['errors']['transcription'] == tooLongError
        assert resp['errors']['phoneticTranscription'] == tooLongError
        assert resp['errors']['narrowPhoneticTranscription'] == tooLongError
        assert resp['errors']['morphemeBreak'] == tooLongError
        assert resp['errors']['morphemeGloss'] == tooLongError
        assert resp['errors']['status'] == \
            u"Value must be one of: tested; requires testing (not u'invalid status value')"
        assert newFormCount == formCount

        # Add some default application settings and set
        # app_globals.applicationSettings.
        applicationSettings = h.generateDefaultApplicationSettings()
        Session.add(applicationSettings)
        Session.commit()
        extra_environ = self.extra_environ_admin.copy()
        extra_environ['test.applicationSettings'] = True
        badGrammaticality = u'***'
        availableGrammaticalities = u', '.join(
            [u''] + applicationSettings.grammaticalities.split(','))
        goodGrammaticality = applicationSettings.grammaticalities.split(',')[0]

        # Create a form with an invalid grammaticality
        params = self.createParams.copy()
        params.update({
            'transcription': u'test create invalid transcription',
            'grammaticality': badGrammaticality,
            'translations': [{'transcription': 'test create invalid translation',
                         'grammaticality': badGrammaticality}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ=extra_environ, status=400)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        assert resp['errors']['grammaticality'] == \
            u'The grammaticality submitted does not match any of the available options.'
        assert resp['errors']['translations'] == \
            u'At least one submitted translation grammaticality does not match any of the available options.'
        assert newFormCount == formCount

        # Create a form with a valid grammaticality
        params = self.createParams.copy()
        params.update({
            'transcription': u'test create invalid transcription',
            'grammaticality': goodGrammaticality,
            'translations': [{'transcription': 'test create invalid translation',
                         'grammaticality': goodGrammaticality}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ=extra_environ)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        assert resp['grammaticality'] == goodGrammaticality
        assert goodGrammaticality in [t['grammaticality'] for t in
                                      resp['translations']]
        assert newFormCount == formCount + 1

        # Create a form with some invalid many-to-one data, i.e., elicitation
        # method, speaker, enterer, etc.
        badId = 109
        badInt = u'abc'
        params = self.createParams.copy()
        params.update({
            'transcription': u'test create invalid transcription',
            'translations': [{'transcription': 'test create invalid translation',
                         'grammaticality': u''}],
            'elicitationMethod': badId,
            'syntacticCategory': badInt,
            'speaker': badId,
            'elicitor': badInt,
            'verifier': badId,
            'source': badInt
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ=extra_environ, status=400)
        resp = json.loads(response.body)
        formCount = newFormCount
        newFormCount = Session.query(model.Form).count()
        assert response.content_type == 'application/json'
        assert resp['errors']['elicitationMethod'] == \
            u'There is no elicitation method with id %d.' % badId
        assert resp['errors']['speaker'] == \
            u'There is no speaker with id %d.' % badId
        assert resp['errors']['verifier'] == \
            u'There is no user with id %d.' % badId
        assert resp['errors']['syntacticCategory'] == u'Please enter an integer value'
        assert resp['errors']['elicitor'] == u'Please enter an integer value'
        assert resp['errors']['source'] == u'Please enter an integer value'
        assert newFormCount == formCount

        # Now create a form with some *valid* many-to-one data, i.e.,
        # elicitation method, speaker, elicitor, etc.
        elicitationMethod = h.generateDefaultElicitationMethod()
        S = h.generateSSyntacticCategory()
        speaker = h.generateDefaultSpeaker()
        source = h.generateDefaultSource()
        Session.add_all([elicitationMethod, S, speaker, source])
        Session.commit()
        sourceId = source.id
        sourceYear = source.year
        contributor = Session.query(model.User).filter(
            model.User.role==u'contributor').first()
        administrator = Session.query(model.User).filter(
            model.User.role==u'administrator').first()
        params = self.createParams.copy()
        params.update({
            'transcription': u'test create invalid transcription',
            'translations': [{'transcription': 'test create invalid translation',
                         'grammaticality': u''}],
            'elicitationMethod': h.getElicitationMethods()[0].id,
            'syntacticCategory': h.getSyntacticCategories()[0].id,
            'speaker': h.getSpeakers()[0].id,
            'elicitor': contributor.id,
            'verifier': administrator.id,
            'source': sourceId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ=extra_environ)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        assert resp['elicitationMethod']['name'] == elicitationMethod.name
        assert resp['source']['year'] == sourceYear    # etc. ...
        assert newFormCount == formCount + 1

    #@nottest
    def test_create_with_inventory_validation(self):
        """Tests that POST /forms correctly applies inventory-based validation on form creation attempts."""

        # Configure the application settings with some VERY STRICT inventory-
        # based validation settings.
        orthography = model.Orthography()
        orthography.name = u'Test Orthography'
        orthography.orthography = u'o,O'
        orthography.lowercase = True
        orthography.initialGlottalStops = True
        Session.add(orthography)
        Session.commit()
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.orthographicValidation = u'Error'
        applicationSettings.narrowPhoneticInventory = u'n,p,N,P'
        applicationSettings.narrowPhoneticValidation = u'Error'
        applicationSettings.broadPhoneticInventory = u'b,p,B,P'
        applicationSettings.broadPhoneticValidation = u'Error'
        applicationSettings.morphemeBreakIsOrthographic = False
        applicationSettings.morphemeBreakValidation = u'Error'
        applicationSettings.phonemicInventory = u'p,i,P,I'
        applicationSettings.storageOrthography = h.getOrthographies()[0]
        Session.add(applicationSettings)
        Session.commit()

        # Here we indirectly cause app_globals.applicationSettings to be set to
        # an ApplicationSettings instance.  See lib.base.BaseController().__before__/__after__.
        extra_environ = self.extra_environ_admin.copy()
        extra_environ['test.applicationSettings'] = True

        # Create a form with all invalid transcriptions.
        params = self.createParams.copy()
        params.update({
            'narrowPhoneticTranscription': u'test narrow phonetic transcription validation',
            'phoneticTranscription': u'test broad phonetic transcription validation',
            'transcription': u'test orthographic transcription validation',
            'morphemeBreak': u'test morpheme break validation',
            'translations': [{'transcription': u'test validation translation', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ, status=400)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert u'The orthographic transcription you have entered is not valid' \
            in resp['errors']['transcription']
        assert u'The broad phonetic transcription you have entered is not valid' \
            in resp['errors']['phoneticTranscription']
        assert u'The narrow phonetic transcription you have entered is not valid' \
            in resp['errors']['narrowPhoneticTranscription']
        assert u'The morpheme segmentation you have entered is not valid' \
            in resp['errors']['morphemeBreak']
        assert u'phonemic inventory' in resp['errors']['morphemeBreak']
        assert formCount == 0

        # Create a form with some invalid and some valid transcriptions.
        params = self.createParams.copy()
        params.update({
            'narrowPhoneticTranscription': u'np NP n P N p',    # Now it's valid
            'phoneticTranscription': u'test broad phonetic transcription validation',
            'transcription': u'',
            'morphemeBreak': u'test morpheme break validation',
            'translations': [{'transcription': u'test validation translation', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ, status=400)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert resp['errors']['transcription'] == u'Please enter a value'
        assert u'The broad phonetic transcription you have entered is not valid' \
            in resp['errors']['phoneticTranscription']
        assert 'narrowPhoneticTranscription' not in resp
        assert u'The morpheme segmentation you have entered is not valid' \
            in resp['errors']['morphemeBreak']
        assert formCount == 0

        # Now change the validation settings to make some transcriptions valid.
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.orthographicValidation = u'Warning'
        applicationSettings.narrowPhoneticInventory = u'n,p,N,P'
        applicationSettings.narrowPhoneticValidation = u'Error'
        applicationSettings.broadPhoneticInventory = u'b,p,B,P'
        applicationSettings.broadPhoneticValidation = u'None'
        applicationSettings.morphemeBreakIsOrthographic = True
        applicationSettings.morphemeBreakValidation = u'Error'
        applicationSettings.phonemicInventory = u'p,i,P,I'
        applicationSettings.storageOrthography = h.getOrthographies()[0]
        Session.add(applicationSettings)
        Session.commit()
        params = self.createParams.copy()
        params.update({
            'narrowPhoneticTranscription': u'test narrow phonetic transcription validation',
            'phoneticTranscription': u'test broad phonetic transcription validation',
            'transcription': u'test orthographic transcription validation',
            'morphemeBreak': u'test morpheme break validation',
            'translations': [{'transcription': u'test validation translation', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ, status=400)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert u'transcription' not in resp['errors']
        assert u'phoneticTranscription' not in resp['errors']
        assert u'The narrow phonetic transcription you have entered is not valid' \
            in resp['errors']['narrowPhoneticTranscription']
        assert u'The morpheme segmentation you have entered is not valid' \
            in resp['errors']['morphemeBreak']
        assert formCount == 0

        # Now perform a successful create by making the narrow phonetic and
        # morpheme break fields valid according to the relevant inventories.
        params = self.createParams.copy()
        params.update({
            'narrowPhoneticTranscription': u'n p NP N P NNNN pPPP pnNpP   ',
            'phoneticTranscription': u'test broad phonetic transcription validation',
            'transcription': u'test orthographic transcription validation',
            'morphemeBreak': u'OOO ooo OOO   o',
            'translations': [{'transcription': u'test validation translation', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert u'errors' not in resp
        assert formCount == 1

        # Create a foreign word form (i.e., one tagged with a foreign word tag).
        # Such forms should be able to violate the inventory-based validation
        # restrictions.
        # We need to ensure that updateApplicationSettingsIfFormIsForeignWord
        # is updating the global Inventory objects with the foreign word.
        # The key 'test.applicationSettings' in the environ causes application
        # settings to be deleted from app_globals after each request; to prevent
        # this we pass in 'test.retainApplicationSettings' also.
        retain_extra_environ = extra_environ.copy()
        retain_extra_environ['test.retainApplicationSettings'] = True
        foreignWordTag = h.generateForeignWordTag()
        Session.add(foreignWordTag)
        Session.commit()
        params = self.createParams.copy()
        params.update({
            'narrowPhoneticTranscription': u'f`ore_n',
            'phoneticTranscription': u'foren',
            'transcription': u'foreign',
            'morphemeBreak': u'foreign',
            'translations': [{'transcription': u'foreign translation', 'grammaticality': u''}],
            'tags': [h.getForeignWordTag().id]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 retain_extra_environ)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        applicationSettings = response.g.applicationSettings
        assert 'f`ore_n' in applicationSettings.narrowPhoneticInventory.inputList
        assert 'foren' in applicationSettings.broadPhoneticInventory.inputList
        assert 'foreign' in applicationSettings.morphemeBreakInventory.inputList
        assert 'foreign' in applicationSettings.orthographicInventory.inputList
        assert u'errors' not in resp
        assert formCount == 2

        # Now create a form that would violate inventory-based validation rules
        # but is nevertheless accepted because the violations are foreign words.
        params = self.createParams.copy()
        params.update({
            'narrowPhoneticTranscription': u'n f`ore_np',
            'phoneticTranscription': u'b p',
            'transcription': u'o O',
            'morphemeBreak': u'o-foreign-O',
            'translations': [{'transcription': u'sentence containing foreign word', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert u'errors' not in resp
        assert formCount == 3

    #@nottest
    def test_relational_attribute_creation(self):
        """Tests that POST/PUT create and update many-to-many data correctly."""

        formCount = Session.query(model.Form).count()

        # Add an empty application settings and two syntactic categories.
        restrictedTag = h.generateRestrictedTag()
        foreignWordTag = h.generateForeignWordTag()
        file1Name = u'test_relational_file'
        file2Name = u'test_relational_file_2'
        file1 = h.generateDefaultFile()
        file1.name = file1Name
        file2 = h.generateDefaultFile()
        file2.name = file2Name
        Session.add_all([restrictedTag, foreignWordTag,
                              file1, file2])
        Session.commit()

        # Create a form with some files and tags.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test relational transcription',
            'translations': [{'transcription': u'test relational translation',
                         'grammaticality': u''}],
            'tags': [t.id for t in h.getTags()],
            'files': [f.id for f in h.getFiles()]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin)
        newFormCount = Session.query(model.Form).count()
        resp = json.loads(response.body)
        formFiles = Session.query(model.FormFile)
        createdFormId = resp['id']
        assert newFormCount == formCount + 1
        assert len([ff.form_id for ff in formFiles
                    if ff.form_id == resp['id']]) == 2
        assert file1Name in [f['name'] for f in resp['files']]
        assert file2Name in [f['name'] for f in resp['files']]
        assert restrictedTag.name in [t['name'] for t in resp['tags']]

        # Attempt to update the form we just created but don't change the tags.
        # Expect the update attempt to fail.
        tags = [t.id for t in h.getTags()]
        tags.reverse()
        files = [f.id for f in h.getFiles()]
        files.reverse()
        params = self.createParams.copy()
        params.update({
            'transcription': u'test relational transcription',
            'translations': [{'transcription': u'test relational translation',
                         'grammaticality': u''}],
            'tags': tags,
            'files': files
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=createdFormId), params,
                        self.json_headers, self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        assert resp['error'] == \
            u'The update request failed because the submitted data were not new.'

        # Now update by removing one of the files and expect success.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test relational transcription',
            'translations': [{'transcription': u'test relational translation',
                         'grammaticality': u''}],
            'tags': tags,
            'files': files[0:1]
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=createdFormId), params,
                        self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        formCount = newFormCount
        newFormCount = Session.query(model.Form).count()
        assert newFormCount == formCount
        assert len(resp['files']) == 1
        assert restrictedTag.name in [t['name'] for t in resp['tags']]
        assert foreignWordTag.name in [t['name'] for t in resp['tags']]

        # Attempt to create a form with some *invalid* files and tags and fail.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test relational transcription invalid',
            'translations': [{'transcription': u'test relational translation invalid',
                         'grammaticality': u''}],
            'tags': [1000, 9875, u'abcdef'],
            'files': [44, u'1t']
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin, status=400)
        formCount = newFormCount
        newFormCount = Session.query(model.Form).count()
        resp = json.loads(response.body)
        assert newFormCount == formCount
        assert u'Please enter an integer value' in resp['errors']['files']
        assert u'There is no file with id 44.' in resp['errors']['files']
        assert u'There is no tag with id 1000.' in resp['errors']['tags']
        assert u'There is no tag with id 9875.' in resp['errors']['tags']
        assert u'Please enter an integer value' in resp['errors']['tags']

    #@nottest
    def test_relational_restrictions(self):
        """Tests that the restricted tag works correctly with respect to relational attributes of forms.

        That is, tests that (a) form.files does not return restricted files to
        restricted users and (b) a restricted user cannot append a restricted
        form to file.forms."""

        admin = self.extra_environ_admin.copy()
        admin.update({'test.applicationSettings': True})
        contrib = self.extra_environ_contrib.copy()
        contrib.update({'test.applicationSettings': True})

        # Create a test form.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test',
            'translations': [{'transcription': u'test_create_translation', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 admin)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert resp['transcription'] == u'test'
        assert formCount == 1

        # Now create the restricted tag.
        restrictedTag = h.generateRestrictedTag()
        Session.add(restrictedTag)
        Session.commit()
        restrictedTagId = restrictedTag.id

        # Then create two files, one restricted and one not.
        wavFilePath = os.path.join(self.testFilesPath, 'old_test.wav')
        wavFileSize = os.path.getsize(wavFilePath)
        wavFileBase64 = encodestring(open(wavFilePath).read())

        params = self.createFileParams.copy()
        params.update({
            'filename': u'restrictedFile.wav',
            'base64EncodedFile': wavFileBase64,
            'tags': [restrictedTagId]
        })
        params = json.dumps(params)
        response = self.app.post(url('files'), params, self.json_headers,
                                 admin)
        resp = json.loads(response.body)
        restrictedFileId = resp['id']

        params = self.createFileParams.copy()
        params.update({
            'filename': u'unrestrictedFile.wav',
            'base64EncodedFile': wavFileBase64
        })
        params = json.dumps(params)
        response = self.app.post(url('files'), params, self.json_headers,
                                 admin)
        resp = json.loads(response.body)
        unrestrictedFileId = resp['id']

        # Now, as a (restricted) contributor, attempt to create a form and
        # associate it to a restricted file -- expect to fail.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test',
            'translations': [{'transcription': u'test_create_translation', 'grammaticality': u''}],
            'files': [restrictedFileId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 contrib, status=400)
        resp = json.loads(response.body)
        assert u'You are not authorized to access the file with id %d.' % restrictedFileId in \
            resp['errors']['files']

        # Now, as a (restricted) contributor, attempt to create a form and
        # associate it to an unrestricted file -- expect to succeed.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test',
            'translations': [{'transcription': u'test_create_translation', 'grammaticality': u''}],
            'files': [unrestrictedFileId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 contrib)
        resp = json.loads(response.body)
        unrestrictedFormId = resp['id']
        assert resp['transcription'] == u'test'
        assert resp['files'][0]['name'] == u'unrestrictedFile.wav'

        # Now, as a(n unrestricted) administrator, attempt to create a form and
        # associate it to a restricted file -- expect (a) to succeed and (b) to
        # find that the form is now restricted.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test',
            'translations': [{'transcription': u'test_create_translation', 'grammaticality': u''}],
            'files': [restrictedFileId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, admin)
        resp = json.loads(response.body)
        indirectlyRestrictedFormId = resp['id']
        assert resp['transcription'] == u'test'
        assert resp['files'][0]['name'] == u'restrictedFile.wav'
        assert u'restricted' in [t['name'] for t in resp['tags']]

        # Now show that the indirectly restricted forms are inaccessible to
        # unrestricted users.
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=contrib)
        resp = json.loads(response.body)
        assert indirectlyRestrictedFormId not in [f['id'] for f in resp]

        # Now, as a(n unrestricted) administrator, create a form.
        unrestrictedFormParams = self.createParams.copy()
        unrestrictedFormParams.update({
            'transcription': u'test',
            'translations': [{'transcription': u'test_create_translation', 'grammaticality': u''}]
        })
        params = json.dumps(unrestrictedFormParams)
        response = self.app.post(url('forms'), params, self.json_headers, admin)
        resp = json.loads(response.body)
        unrestrictedFormId = resp['id']
        assert resp['transcription'] == u'test'

        # As a restricted contributor, attempt to update the unrestricted form
        # just created by associating it to a restricted file -- expect to fail.
        unrestrictedFormParams.update({'files': [restrictedFileId]})
        params = json.dumps(unrestrictedFormParams)
        response = self.app.put(url('form', id=unrestrictedFormId), params,
                                self.json_headers, contrib, status=400)
        resp = json.loads(response.body)
        assert u'You are not authorized to access the file with id %d.' % restrictedFileId in \
            resp['errors']['files']

        # As an unrestricted administrator, attempt to update an unrestricted form
        # by associating it to a restricted file -- expect to succeed.
        response = self.app.put(url('form', id=unrestrictedFormId), params,
                                self.json_headers, admin)
        resp = json.loads(response.body)
        assert resp['id'] == unrestrictedFormId
        assert u'restricted' in [t['name'] for t in resp['tags']]

        # Now show that the newly indirectly restricted form is also
        # inaccessible to an unrestricted user.
        response = self.app.get(url('form', id=unrestrictedFormId),
                headers=self.json_headers, extra_environ=contrib, status=403)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert resp['error'] == u'You are not authorized to access this resource.'

    #@nottest
    def test_new(self):
        """Tests that GET /form/new returns an appropriate JSON object for creating a new OLD form.

        The properties of the JSON object are 'grammaticalities',
        'elicitationMethods', 'tags', 'syntacticCategories', 'speakers',
        'users' and 'sources' and their values are arrays/lists.
        """

        # Unauthorized user ('viewer') should return a 401 status code on the
        # new action, which requires a 'contributor' or an 'administrator'.
        extra_environ = {'test.authentication.role': 'viewer'}
        response = self.app.get(url('new_form'), extra_environ=extra_environ,
                                status=403)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert resp['error'] == u'You are not authorized to access this resource.'

        # Add some test data to the database.
        applicationSettings = h.generateDefaultApplicationSettings()
        elicitationMethod = h.generateDefaultElicitationMethod()
        foreignWordTag = h.generateForeignWordTag()
        restrictedTag = h.generateRestrictedTag()
        N = h.generateNSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        S = h.generateSSyntacticCategory()
        speaker = h.generateDefaultSpeaker()
        source = h.generateDefaultSource()
        Session.add_all([applicationSettings, elicitationMethod,
                    foreignWordTag, restrictedTag, N, Num, S, speaker, source])
        Session.commit()

        # Get the data currently in the db (see websetup.py for the test data).
        data = {
            'grammaticalities': h.getGrammaticalities(),
            'elicitationMethods': h.getMiniDictsGetter('ElicitationMethod')(),
            'tags': h.getMiniDictsGetter('Tag')(),
            'syntacticCategories': h.getMiniDictsGetter('SyntacticCategory')(),
            'speakers': h.getMiniDictsGetter('Speaker')(),
            'users': h.getMiniDictsGetter('User')(),
            'sources': h.getMiniDictsGetter('Source')()
        }

        # JSON.stringify and then re-Python-ify the data.  This is what the data
        # should look like in the response to a simulated GET request.
        data = json.loads(json.dumps(data, cls=h.JSONOLDEncoder))

        # GET /form/new without params.  Without any GET params, /form/new
        # should return a JSON array for every store.
        response = self.app.get(url('new_form'),
                                extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert resp['grammaticalities'] == data['grammaticalities']
        assert resp['elicitationMethods'] == data['elicitationMethods']
        assert resp['tags'] == data['tags']
        assert resp['syntacticCategories'] == data['syntacticCategories']
        assert resp['speakers'] == data['speakers']
        assert resp['users'] == data['users']
        assert resp['sources'] == data['sources']
        assert response.content_type == 'application/json'

        # GET /new_form with params.  Param values are treated as strings, not
        # JSON.  If any params are specified, the default is to return a JSON
        # array corresponding to store for the param.  There are three cases
        # that will result in an empty JSON array being returned:
        # 1. the param is not specified
        # 2. the value of the specified param is an empty string
        # 3. the value of the specified param is an ISO 8601 UTC datetime
        #    string that matches the most recent datetimeModified value of the
        #    store in question.
        params = {
            # Value is empty string: 'grammaticalities' will not be in response.
            'grammaticalities': '',
            # Value is any string: 'elicitationMethods' will be in response.
            'elicitationMethods': 'anything can go here!',
            # Value is ISO 8601 UTC datetime string that does not match the most
            # recent Tag.datetimeModified value: 'tags' *will* be in
            # response.
            'tags': datetime.datetime.utcnow().isoformat(),
            # Value is ISO 8601 UTC datetime string that does match the most
            # recent SyntacticCategory.datetimeModified value:
            # 'syntacticCategories' will *not* be in response.
            'syntacticCategories': h.getMostRecentModificationDatetime(
                'SyntacticCategory').isoformat()
        }
        response = self.app.get(url('new_form'), params,
                                extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert resp['elicitationMethods'] == data['elicitationMethods']
        assert resp['tags'] == data['tags']
        assert resp['grammaticalities'] == []
        assert resp['syntacticCategories'] == []
        assert resp['speakers'] == []
        assert resp['users'] == []
        assert resp['sources'] == []

    #@nottest
    def test_update(self):
        """Tests that PUT /forms/id correctly updates an existing form."""

        formCount = Session.query(model.Form).count()

        # Add the default application settings and the restricted tag.
        restrictedTag = h.generateRestrictedTag()
        applicationSettings = h.generateDefaultApplicationSettings()
        Session.add_all([applicationSettings, restrictedTag])
        Session.commit()
        restrictedTag = h.getRestrictedTag()

        # Create a form to update.
        params = self.createParams.copy()
        originalTranscription = u'test_update_transcription'
        originalTranslation = u'test_update_translation'
        params.update({
            'transcription': originalTranscription,
            'translations': [{'transcription': originalTranslation, 'grammaticality': u''}],
            'tags': [restrictedTag.id]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 self.extra_environ_admin)
        resp = json.loads(response.body)
        id = int(resp['id'])
        newFormCount = Session.query(model.Form).count()
        assert resp['transcription'] == originalTranscription
        assert resp['translations'][0]['transcription'] == originalTranslation
        assert newFormCount == formCount + 1

        # As a viewer, attempt to update the restricted form we just created.
        # Expect to fail.
        extra_environ = {'test.authentication.role': 'viewer',
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'transcription': u'Updated!',
            'translations': [{'transcription': u'test_update_translation', 'grammaticality': u''}],
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=id), params,
            self.json_headers, extra_environ, status=403)
        resp = json.loads(response.body)
        assert resp['error'] == u'You are not authorized to access this resource.'

        # As an administrator now, update the form just created and expect to
        # succeed.
        origBackupCount = Session.query(model.FormBackup).count()
        params = self.createParams.copy()
        params.update({
            'transcription': u'Updated!',
            'translations': [{'transcription': u'test_update_translation', 'grammaticality': u''}],
            'morphemeBreak': u'a-b',
            'morphemeGloss': u'c-d',
            'status': u'requires testing'
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=id), params,
                                self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        newBackupCount = Session.query(model.FormBackup).count()
        morphemeBreakIDsOfWord = resp['morphemeBreakIDs']
        assert resp['transcription'] == u'Updated!'
        assert resp['translations'][0]['transcription'] == u'test_update_translation'
        assert resp['morphemeBreak'] == u'a-b'
        assert resp['morphemeGloss'] == u'c-d'
        assert resp['morphemeBreakIDs'] == [[[], []]]
        assert resp['morphemeGlossIDs'] == [[[], []]]
        assert resp['status'] == u'requires testing'
        assert newFormCount == formCount + 1
        assert origBackupCount + 1 == newBackupCount
        backup = Session.query(model.FormBackup).filter(
            model.FormBackup.UUID==unicode(
            resp['UUID'])).order_by(
            desc(model.FormBackup.id)).first()
        assert backup.datetimeModified.isoformat() == resp['datetimeModified']
        assert backup.transcription == originalTranscription
        assert response.content_type == 'application/json'

        # Attempt an update with no new data.  Expect a 400 error
        # and response['errors'] = {'no change': The update request failed
        # because the submitted data were not new.'}.
        origBackupCount = Session.query(model.FormBackup).count()
        response = self.app.put(url('form', id=id), params, self.json_headers,
                                self.extra_environ_admin, status=400)
        newBackupCount = Session.query(model.FormBackup).count()
        resp = json.loads(response.body)
        assert origBackupCount == newBackupCount
        assert u'the submitted data were not new' in resp['error']

        # Now create a lexical form matching one of the morpheme-form/morpheme-gloss
        # pairs in the above form.  The call to updateFormsContainingThisFormAsMorpheme
        # in the create action will cause the morphemeBreakIDs and
        # morphemeGlossIDs attributes of the phrasal form to change.
        origBackupCount = Session.query(model.FormBackup).count()
        updatedWord = Session.query(model.Form).get(id)
        assert json.loads(updatedWord.morphemeBreakIDs) == morphemeBreakIDsOfWord
        newParams = self.createParams.copy()
        newParams.update({
            'transcription': u'a',
            'translations': [{'transcription': u'lexical', 'grammaticality': u''}],
            'morphemeBreak': u'a',
            'morphemeGloss': u'c'
        })
        newParams = json.dumps(newParams)
        response = self.app.post(url('forms'), newParams, self.json_headers,
                                 self.extra_environ_admin)
        updatedWord = Session.query(model.Form).get(id)
        newMorphemeBreakIDsOfWord = json.loads(updatedWord.morphemeBreakIDs)
        newMorphemeGlossIDsOfWord = json.loads(updatedWord.morphemeGlossIDs)
        newBackupCount = Session.query(model.FormBackup).count()
        assert newMorphemeBreakIDsOfWord != morphemeBreakIDsOfWord
        assert origBackupCount + 1 == newBackupCount
        assert newMorphemeBreakIDsOfWord[0][0][0][1] == u'c'
        assert newMorphemeBreakIDsOfWord[0][0][0][2] == None
        assert newMorphemeGlossIDsOfWord[0][0][0][1] == u'a'
        assert newMorphemeGlossIDsOfWord[0][0][0][2] == None

        # A vacuous update on the word will fail since the updating was accomplished
        # via the creation of the a/c morpheme.
        response = self.app.put(url('form', id=id), params, self.json_headers,
                                self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        assert u'the submitted data were not new' in resp['error']

        # Again update our form, this time making it into a foreign word.
        # Updating a form into a foreign word should update the Inventory
        # objects in app_globals.
        # First we create an application settings with some VERY STRICT
        # inventory-based validation settings.  Also we add a foreign word tag.
        orthography = model.Orthography()
        orthography.name = u'Test Orthography'
        orthography.orthography = u'o,O'
        orthography.lowercase = True
        orthography.initialGlottalStops = True
        Session.add(orthography)
        Session.commit()
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.orthographicValidation = u'Error'
        applicationSettings.narrowPhoneticInventory = u'n,p,N,P'
        applicationSettings.narrowPhoneticValidation = u'Error'
        applicationSettings.broadPhoneticInventory = u'b,p,B,P'
        applicationSettings.broadPhoneticValidation = u'Error'
        applicationSettings.morphemeBreakIsOrthographic = False
        applicationSettings.morphemeBreakValidation = u'Error'
        applicationSettings.phonemicInventory = u'p,i,P,I'
        applicationSettings.storageOrthography = h.getOrthographies()[0]
        foreignWordTag = h.generateForeignWordTag()
        Session.add_all([applicationSettings, foreignWordTag])
        Session.commit()
        # Here we indirectly cause app_globals.applicationSettings to be set to
        # an h.ApplicationSettings instance that has our model.ApplicationSettings
        # instance as an attribute.  We do this with some special keys in environ.
        # We need to ensure that updateApplicationSettingsIfFormIsForeignWord
        # is updating the global Inventory objects with the foreign word.
        # The key 'test.applicationSettings' in the environ causes application
        # settings to be deleted from app_globals after each request; to prevent
        # this we pass in 'test.retainApplicationSettings' also.
        extra_environ = self.extra_environ_admin.copy()
        extra_environ['test.applicationSettings'] = True
        extra_environ['test.retainApplicationSettings'] = True
        # Now we update using the same params as before, only this time we tag
        # as a foreign word.  
        params = self.createParams.copy()
        params.update({
            'transcription': u'Updated!',
            'translations': [{'transcription': u'test_update_translation', 'grammaticality': u''}],
            'tags': [h.getForeignWordTag().id],
            'morphemeBreak': u'a-b',
            'morphemeGloss': u'c-d'
        })
        params = json.dumps(params)
        # There should be no app_globals.applicationSettings in the last response.
        assert not hasattr(response.g, 'applicationSettings')
        response = self.app.put(url('form', id=id), params, self.json_headers,
                                extra_environ)
        resp = json.loads(response.body)
        applicationSettings = response.g.applicationSettings
        # This is how we know that updateApplicationSettingsIfFormIsForeignWord
        # is working
        assert 'a-b' in applicationSettings.morphemeBreakInventory.inputList
        assert 'Updated!' in applicationSettings.orthographicInventory.inputList
        assert u'errors' not in resp

        # Now update our form by adding a many-to-one datum, viz. a speaker
        speaker = h.generateDefaultSpeaker()
        Session.add(speaker)
        Session.commit()
        speaker = h.getSpeakers()[0]
        params = self.createParams.copy()
        params.update({
            'transcription': u'oO',
            'translations': [{'transcription': 'Updated again translation',
                         'grammaticality': u''}],
            'speaker': speaker.id,
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=id), params, self.json_headers,
                                 extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert resp['speaker']['firstName'] == speaker.firstName

    #@nottest
    def test_delete(self):
        """Tests that DELETE /forms/id deletes the form with id=id and returns a JSON representation.

        If the id is invalid or unspecified, then JSON null or a 404 status code
        are returned, respectively.
        """

        originalContributorId = Session.query(model.User).filter(
            model.User.role==u'contributor').first().id
        # Add some objects to the db: a default application settings, a speaker,
        # a tag, a file ...
        applicationSettings = h.generateDefaultApplicationSettings()
        speaker = h.generateDefaultSpeaker()
        myContributor = h.generateDefaultUser()
        myContributor.username = u'uniqueusername'
        tag = model.Tag()
        tag.name = u'default tag'
        file = h.generateDefaultFile()
        Session.add_all([applicationSettings, speaker, myContributor, tag, file])
        Session.commit()
        myContributor = Session.query(model.User).filter(
            model.User.username==u'uniqueusername').first()
        myContributorId = myContributor.id
        tagId = tag.id
        fileId = file.id
        speakerId = speaker.id
        speakerFirstName = speaker.firstName

        # Count the original number of forms and formBackups.
        formCount = Session.query(model.Form).count()
        formBackupCount = Session.query(model.FormBackup).count()

        # First, as myContributor, create a form to delete.
        extra_environ = {'test.authentication.id': myContributorId,
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'transcription': u'test_delete_transcription',
            'translations': [{'transcription': u'test_delete_translation', 'grammaticality': u''}],
            'speaker': unicode(speaker.id),
            'tags': [tagId],
            'files': [fileId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)
        resp = json.loads(response.body)
        toDeleteId = resp['id']
        assert resp['transcription'] == u'test_delete_transcription'
        assert resp['translations'][0]['transcription'] == u'test_delete_translation'
        assert resp['tags'][0]['name'] == u'default tag'
        assert resp['files'][0]['name'] == u'test_file_name'

        # Query the Translation from the db and expect it to be present.
        translation = Session.query(model.Translation).get(resp['translations'][0]['id'])
        assert translation.transcription == u'test_delete_translation'

        # Now count the forms and formBackups.
        newFormCount = Session.query(model.Form).count()
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormCount == formCount + 1
        assert newFormBackupCount == formBackupCount

        # Now, as the default contributor, attempt to delete the myContributor-
        # entered form we just created and expect to fail.
        extra_environ = {'test.authentication.id': originalContributorId,
                         'test.applicationSettings': True}
        response = self.app.delete(url('form', id=toDeleteId),
                                   extra_environ=extra_environ, status=403)
        resp = json.loads(response.body)
        assert resp['error'] == u'You are not authorized to access this resource.'

        # As myContributor, attempt to delete the form we just created and
        # expect to succeed.  Show that translations get deleted when forms do but
        # many-to-many relations (e.g., tags and files) and many-to-one relations
        # (e.g., speakers) do not.
        extra_environ = {'test.authentication.id': myContributorId,
                         'test.applicationSettings': True}
        response = self.app.delete(url('form', id=toDeleteId),
                                   extra_environ=extra_environ)
        resp = json.loads(response.body)
        newFormCount = Session.query(model.Form).count()
        newFormBackupCount = Session.query(model.FormBackup).count()
        translationOfDeletedForm = Session.query(model.Translation).get(
            resp['translations'][0]['id'])
        tagOfDeletedForm = Session.query(model.Tag).get(
            resp['tags'][0]['id'])
        fileOfDeletedForm = Session.query(model.File).get(
            resp['files'][0]['id'])
        speakerOfDeletedForm = Session.query(model.Speaker).get(
            resp['speaker']['id'])
        assert translationOfDeletedForm is None
        assert isinstance(tagOfDeletedForm, model.Tag)
        assert isinstance(fileOfDeletedForm, model.File)
        assert isinstance(speakerOfDeletedForm, model.Speaker)
        assert newFormCount == formCount
        assert newFormBackupCount == formBackupCount + 1
        assert response.content_type == 'application/json'

        # The deleted form will be returned to us, so the assertions from above
        # should still hold true.
        assert resp['transcription'] == u'test_delete_transcription'
        assert resp['translations'][0]['transcription'] == u'test_delete_translation'

        # Trying to get the deleted form from the db should return None
        deletedForm = Session.query(model.Form).get(toDeleteId)
        assert deletedForm == None

        # The backed up form should have the deleted form's attributes
        backedUpForm = Session.query(model.FormBackup).filter(
            model.FormBackup.UUID==unicode(resp['UUID'])).first()
        assert backedUpForm.transcription == resp['transcription']
        backuper = json.loads(unicode(backedUpForm.backuper))
        assert backuper['firstName'] == u'test user first name'
        backedUpSpeaker = json.loads(unicode(backedUpForm.speaker))
        assert backedUpSpeaker['firstName'] == speakerFirstName
        assert backedUpForm.datetimeEntered.isoformat() == resp['datetimeEntered']
        assert backedUpForm.UUID == resp['UUID']

        # Delete with an invalid id
        id = 9999999999999
        response = self.app.delete(url('form', id=id),
            headers=self.json_headers, extra_environ=self.extra_environ_admin,
            status=404)
        assert response.content_type == 'application/json'
        assert u'There is no form with id %s' % id in json.loads(response.body)[
            'error']

        # Delete without an id
        response = self.app.delete(url('form', id=''), status=404,
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        assert json.loads(response.body)['error'] == \
            'The resource could not be found.'

    #@nottest
    def test_delete_foreign_word(self):
        """Tests that DELETE /forms/id on a foreign word updates the global Inventory objects correctly."""

        # First create an application settings with some VERY STRICT
        # inventory-based validation settings and a foreign word tag.
        orthography = model.Orthography()
        orthography.name = u'Test Orthography'
        orthography.orthography = u'o,O'
        orthography.lowercase = True
        orthography.initialGlottalStops = True
        Session.add(orthography)
        Session.commit()
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.orthographicValidation = u'Error'
        applicationSettings.narrowPhoneticInventory = u'n,p,N,P'
        applicationSettings.narrowPhoneticValidation = u'Error'
        applicationSettings.broadPhoneticInventory = u'b,p,B,P'
        applicationSettings.broadPhoneticValidation = u'Error'
        applicationSettings.morphemeBreakIsOrthographic = False
        applicationSettings.morphemeBreakValidation = u'Error'
        applicationSettings.phonemicInventory = u'p,i,P,I'
        applicationSettings.storageOrthography = h.getOrthographies()[0]
        foreignWordTag = h.generateForeignWordTag()
        Session.add_all([applicationSettings, foreignWordTag])
        Session.commit()

        # The extra_environ request param causes app_globals.applicationSettings to be set to
        # an h.ApplicationSettings instance that has our model.ApplicationSettings
        # instance as an attribute.  We do this with some special keys in environ.
        # We need to ensure that updateApplicationSettingsIfFormIsForeignWord
        # is updating the global Inventory objects with the foreign word.
        # The key 'test.applicationSettings' in the environ causes application
        # settings to be deleted from app_globals after each request; to prevent
        # this we pass in 'test.retainApplicationSettings' also.
        extra_environ = self.extra_environ_admin.copy()
        extra_environ['test.applicationSettings'] = True
        extra_environ['test.retainApplicationSettings'] = True

        # Then create a foreign word form to delete.
        params = self.createParams.copy()
        params.update({
            'transcription': u'test_delete_transcription',
            'translations': [{'transcription': u'test_delete_translation', 'grammaticality': u''}],
            'tags': [h.getForeignWordTag().id]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)
        resp = json.loads(response.body)
        assert hasattr(response.g, 'applicationSettings')
        applicationSettings = response.g.applicationSettings
        assert resp['transcription'] == u'test_delete_transcription'
        assert resp['translations'][0]['transcription'] == u'test_delete_translation'
        assert 'test_delete_transcription' in applicationSettings.orthographicInventory.inputList

        # Delete the form we just created and observe that the orthographic
        # transcription has been removed from the orthographicInventory object.
        response = self.app.delete(url('form', id=resp['id']),
                                   extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert hasattr(response.g, 'applicationSettings')
        applicationSettings = response.g.applicationSettings
        assert 'test_delete_transcription' not in applicationSettings.orthographicInventory.inputList

    #@nottest
    def test_show(self):
        """Tests that GET /forms/id returns a JSON form object, null or 404
        depending on whether the id is valid, invalid or unspecified,
        respectively.
        """

        # First add a form.
        form = h.generateDefaultForm()
        Session.add(form)
        Session.commit()
        formId = h.getForms()[0].id

        # Invalid id
        id = 100000000000
        response = self.app.get(url('form', id=id),
            headers=self.json_headers, extra_environ=self.extra_environ_admin,
            status=404)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert u'There is no form with id %s' % id in json.loads(response.body)[
            'error']

        # No id
        response = self.app.get(url('form', id=''), status=404,
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        assert json.loads(response.body)['error'] == \
            'The resource could not be found.'

        # Valid id
        response = self.app.get(url('form', id=formId), headers=self.json_headers,
                                extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert resp['transcription'] == u'test transcription'
        assert resp['translations'][0]['transcription'] == u'test translation'
        assert response.content_type == 'application/json'

        # Now test that the restricted tag is working correctly.
        # First get the default contributor's id.
        users = h.getUsers()
        contributorId = [u for u in users if u.role == u'contributor'][0].id

        # Then add another contributor and a restricted tag.
        restrictedTag = h.generateRestrictedTag()
        myContributor = h.generateDefaultUser()
        myContributorFirstName = u'Mycontributor'
        myContributor.firstName = myContributorFirstName
        myContributor.username = u'uniqueusername'
        Session.add_all([restrictedTag, myContributor])
        Session.commit()
        myContributor = Session.query(model.User).filter(
            model.User.firstName == myContributorFirstName).first()
        myContributorId = myContributor.id

        # Then add the default application settings with myContributor as the
        # only unrestricted user.
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.unrestrictedUsers = [myContributor]
        Session.add(applicationSettings)
        Session.commit()
        # Finally, issue a POST request to create the restricted form with
        # the *default* contributor as the enterer.
        extra_environ = {'test.authentication.id': contributorId,
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'transcription': u'test restricted tag transcription',
            'translations': [{'transcription': u'test restricted tag translation',
                         'grammaticality': u''}],
            'tags': [h.getTags()[0].id]    # the restricted tag should be the only one
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                        extra_environ)
        resp = json.loads(response.body)
        restrictedFormId = resp['id']
        # Expectation: the administrator, the default contributor (qua enterer)
        # and the unrestricted myContributor should all be able to view the form.
        # The viewer should get a 403 error when attempting to view this form.
        # An administrator should be able to view this form.
        extra_environ = {'test.authentication.role': 'administrator',
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId),
                        headers=self.json_headers, extra_environ=extra_environ)
        # The default contributor (qua enterer) should be able to view this form.
        extra_environ = {'test.authentication.id': contributorId,
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId),
                        headers=self.json_headers, extra_environ=extra_environ)
        # Mycontributor (an unrestricted user) should be able to view this
        # restricted form.
        extra_environ = {'test.authentication.id': myContributorId,
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId),
                        headers=self.json_headers, extra_environ=extra_environ)
        # A (not unrestricted) viewer should *not* be able to view this form.
        extra_environ = {'test.authentication.role': 'viewer',
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId),
            headers=self.json_headers, extra_environ=extra_environ, status=403)
        # Remove Mycontributor from the unrestricted users list and access will be denied.
        applicationSettings = h.getApplicationSettings()
        applicationSettings.unrestrictedUsers = []
        Session.add(applicationSettings)
        Session.commit()
        # Mycontributor (no longer an unrestricted user) should now *not* be
        # able to view this restricted form.
        extra_environ = {'test.authentication.id': myContributorId,
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId),
            headers=self.json_headers, extra_environ=extra_environ, status=403)
        # Remove the restricted tag from the form and the viewer should now be
        # able to view it too.
        restrictedForm = Session.query(model.Form).get(restrictedFormId)
        restrictedForm.tags = []
        Session.add(restrictedForm)
        Session.commit()
        extra_environ = {'test.authentication.role': 'viewer',
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId),
                        headers=self.json_headers, extra_environ=extra_environ)

    #@nottest
    def test_edit(self):
        """Tests that GET /forms/id/edit returns a JSON object of data necessary to edit the form with id=id.
        
        The JSON object is of the form {'form': {...}, 'data': {...}} or
        {'error': '...'} (with a 404 status code) depending on whether the id is
        valid or invalid/unspecified, respectively.
        """

        # Add the default application settings and the restricted tag.
        applicationSettings = h.generateDefaultApplicationSettings()
        restrictedTag = h.generateRestrictedTag()
        Session.add_all([restrictedTag, applicationSettings])
        Session.commit()
        restrictedTag = h.getRestrictedTag()
        # Create a restricted form.
        form = h.generateDefaultForm()
        form.tags = [restrictedTag]
        Session.add(form)
        Session.commit()
        restrictedForm = h.getForms()[0]
        restrictedFormId = restrictedForm.id

        # As a (not unrestricted) contributor, attempt to call edit on the
        # restricted form and expect to fail.
        extra_environ = {'test.authentication.role': 'contributor',
                         'test.applicationSettings': True}
        response = self.app.get(url('edit_form', id=restrictedFormId),
                                extra_environ=extra_environ, status=403)
        resp = json.loads(response.body)
        assert resp['error'] == u'You are not authorized to access this resource.'

        # Not logged in: expect 401 Unauthorized
        response = self.app.get(url('edit_form', id=restrictedFormId), status=401)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert resp['error'] == u'Authentication is required to access this resource.'

        # Invalid id
        id = 9876544
        response = self.app.get(url('edit_form', id=id),
            headers=self.json_headers, extra_environ=self.extra_environ_admin,
            status=404)
        assert u'There is no form with id %s' % id in json.loads(response.body)[
            'error']

        # No id
        response = self.app.get(url('edit_form', id=''), status=404,
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        assert json.loads(response.body)['error'] == \
            'The resource could not be found.'
        assert response.content_type == 'application/json'

        # Valid id
        response = self.app.get(url('edit_form', id=restrictedFormId),
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert resp['form']['transcription'] == u'test transcription'
        assert resp['form']['translations'][0]['transcription'] == u'test translation'
        assert response.content_type == 'application/json'

        # Valid id with GET params.  Param values are treated as strings, not
        # JSON.  If any params are specified, the default is to return a JSON
        # array corresponding to store for the param.  There are three cases
        # that will result in an empty JSON array being returned:
        # 1. the param is not specified
        # 2. the value of the specified param is an empty string
        # 3. the value of the specified param is an ISO 8601 UTC datetime
        #    string that matches the most recent datetimeModified value of the
        #    store in question.

        # Add some test data to the database.
        applicationSettings = h.generateDefaultApplicationSettings()
        elicitationMethod = h.generateDefaultElicitationMethod()
        foreignWordTag = h.generateForeignWordTag()
        N = h.generateNSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        S = h.generateSSyntacticCategory()
        speaker = h.generateDefaultSpeaker()
        source = h.generateDefaultSource()
        Session.add_all([applicationSettings, elicitationMethod,
            foreignWordTag, N, Num, S, speaker, source])
        Session.commit()

        # Get the data currently in the db (see websetup.py for the test data).
        data = {
            'grammaticalities': h.getGrammaticalities(),
            'elicitationMethods': h.getMiniDictsGetter('ElicitationMethod')(),
            'tags': h.getMiniDictsGetter('Tag')(),
            'syntacticCategories': h.getMiniDictsGetter('SyntacticCategory')(),
            'speakers': h.getMiniDictsGetter('Speaker')(),
            'users': h.getMiniDictsGetter('User')(),
            'sources': h.getMiniDictsGetter('Source')()
        }

        # JSON.stringify and then re-Python-ify the data.  This is what the data
        # should look like in the response to a simulated GET request.
        data = json.loads(json.dumps(data, cls=h.JSONOLDEncoder))

        params = {
            # Value is a non-empty string: 'grammaticalities' will be in response.
            'grammaticalities': 'give me some grammaticalities!',
            # Value is empty string: 'elicitationMethods' will not be in response.
            'elicitationMethods': '',
            # Value is ISO 8601 UTC datetime string that does not match the most
            # recent Source.datetimeModified value: 'sources' *will* be in
            # response.
            'sources': datetime.datetime.utcnow().isoformat(),
            # Value is ISO 8601 UTC datetime string that does match the most
            # recent User.datetimeModified value: 'users' will *not* be in response.
            'users': h.getMostRecentModificationDatetime('User').isoformat()
        }
        response = self.app.get(url('edit_form', id=restrictedFormId), params,
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert resp['data']['elicitationMethods'] == []
        assert resp['data']['tags'] == []
        assert resp['data']['grammaticalities'] == data['grammaticalities']
        assert resp['data']['syntacticCategories'] == []
        assert resp['data']['speakers'] == []
        assert resp['data']['users'] == []
        assert resp['data']['sources'] == data['sources']

        # Invalid id with GET params.  It should still return 'null'.
        params = {
            # If id were valid, this would cause a speakers array to be returned
            # also.
            'speakers': 'True',
        }
        response = self.app.get(url('edit_form', id=id), params,
                            extra_environ=self.extra_environ_admin, status=404)
        assert u'There is no form with id %s' % id in json.loads(response.body)[
            'error']

    #@nottest
    def test_history(self):
        """Tests that GET /forms/id/history returns the form with id=id and its previous incarnations.
        
        The JSON object returned is of the form
        {'form': form, 'previousVersions': [...]}.
        """

        # Add some test data to the database.
        applicationSettings = h.generateDefaultApplicationSettings()
        elicitationMethod = h.generateDefaultElicitationMethod()
        source = h.generateDefaultSource()
        restrictedTag = h.generateRestrictedTag()
        foreignWordTag = h.generateForeignWordTag()
        file1 = h.generateDefaultFile()
        file1.name = u'file1'
        file2 = h.generateDefaultFile()
        file2.name = u'file2'
        N = h.generateNSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        S = h.generateSSyntacticCategory()
        speaker = h.generateDefaultSpeaker()
        Session.add_all([applicationSettings, elicitationMethod, source,
            restrictedTag, foreignWordTag, file1, file2, N, Num, S, speaker])
        Session.commit()

        # Create a restricted form (via request) as the default contributor
        users = h.getUsers()
        contributorId = [u for u in users if u.role==u'contributor'][0].id
        administratorId = [u for u in users if u.role==u'administrator'][0].id
        speakerId = h.getSpeakers()[0].id
        elicitationMethodId = h.getElicitationMethods()[0].id
        syntacticCategoryIds = [sc.id for sc in h.getSyntacticCategories()]
        firstSyntacticCategoryId = syntacticCategoryIds[0]
        lastSyntacticCategoryId = syntacticCategoryIds[-1]
        tagIds = [t.id for t in h.getTags()]
        fileIds = [f.id for f in h.getFiles()]
        restrictedTagId = h.getRestrictedTag().id

        extra_environ = {'test.authentication.role': u'contributor',
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'transcription': u'created by the contributor',
            'translations': [{'transcription': u'created by the contributor', 'grammaticality': u''}],
            'elicitor': contributorId,
            'tags': [restrictedTagId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                        extra_environ)
        formCount = Session.query(model.Form).count()
        resp = json.loads(response.body)
        formId = resp['id']
        formUUID = resp['UUID']
        assert formCount == 1

        # Update our form (via request) as the default administrator
        extra_environ = {'test.authentication.role': u'administrator',
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'grammaticality': u'?',
            'transcription': u'updated by the administrator',
            'translations': [{'transcription': u'updated by the administrator',
                         'grammaticality': u'*'}],
            'morphemeBreak': u'up-dat-ed by the ad-ministr-ator',
            'morphemeGloss': u'up-date-PAST PREP DET PREP-servant-AGT',
            'speaker': speakerId,
            'elicitationMethod': elicitationMethodId,
            'syntacticCategory': firstSyntacticCategoryId,
            'verifier': administratorId,
            'tags': tagIds + [None, u''], # None and u'' ('') will be ignored by forms.updateForm
            'enterer': administratorId  # This should change nothing.
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=formId), params,
                        self.json_headers, extra_environ)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert formCount == 1

        # Finally, update our form (via request) as the default contributor.
        extra_environ = {'test.authentication.role': u'contributor',
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'grammaticality': u'#',
            'transcription': u'updated by the contributor',
            'translations': [{'transcription': u'updated by the contributor',
                         'grammaticality': u'*'}],
            'morphemeBreak': u'up-dat-ed by the ad-ministr-ator',
            'morphemeGloss': u'up-date-PAST PREP DET PREP-servant-AGT',
            'speaker': speakerId,
            'elicitationMethod': elicitationMethodId,
            'syntacticCategory': lastSyntacticCategoryId,
            'tags': tagIds,
            'files': fileIds
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=formId), params,
                        self.json_headers, extra_environ)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        assert formCount == 1

        # Now get the history of this form.
        extra_environ = {'test.authentication.role': u'contributor',
                         'test.applicationSettings': True}
        response = self.app.get(
            url(controller='forms', action='history', id=formId),
            headers=self.json_headers, extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert 'form' in resp
        assert 'previousVersions' in resp
        firstVersion = resp['previousVersions'][1]
        secondVersion = resp['previousVersions'][0]
        currentVersion = resp['form']
        assert firstVersion['transcription'] == u'created by the contributor'
        assert firstVersion['morphemeBreak'] == u''
        assert firstVersion['elicitor']['id'] == contributorId
        assert firstVersion['enterer']['id'] == contributorId
        assert firstVersion['backuper']['id'] == administratorId
        # Should be <; however, MySQL<5.6.4 does not support microseconds in datetimes 
        # so the test will fail/be inconsistent with <
        assert firstVersion['datetimeModified'] <= secondVersion['datetimeModified']
        assert firstVersion['speaker'] == None
        assert firstVersion['elicitationMethod'] == None
        assert firstVersion['syntacticCategory'] == None
        assert firstVersion['verifier'] == None
        assert [t['id'] for t in firstVersion['tags']] == [restrictedTagId]
        assert firstVersion['files'] == []
        assert firstVersion['morphemeBreakIDs'] == None

        assert secondVersion['transcription'] == u'updated by the administrator'
        assert secondVersion['morphemeBreak'] == u'up-dat-ed by the ad-ministr-ator'
        assert secondVersion['elicitor'] == None
        assert secondVersion['enterer']['id'] == contributorId
        assert secondVersion['backuper']['id'] == contributorId
        assert secondVersion['datetimeModified'] == currentVersion['datetimeModified']
        assert secondVersion['speaker']['id'] == speakerId
        assert secondVersion['elicitationMethod']['id'] == elicitationMethodId
        assert secondVersion['syntacticCategory']['id'] == firstSyntacticCategoryId
        assert secondVersion['verifier']['id'] == administratorId
        assert sorted([t['id'] for t in secondVersion['tags']]) == sorted(tagIds)
        assert secondVersion['files'] == []
        assert len(secondVersion['morphemeBreakIDs']) == 4

        assert currentVersion['transcription'] == u'updated by the contributor'
        assert currentVersion['morphemeBreak'] == u'up-dat-ed by the ad-ministr-ator'
        assert currentVersion['elicitor'] == None
        assert currentVersion['enterer']['id'] == contributorId
        assert 'backuper' not in currentVersion
        assert currentVersion['speaker']['id'] == speakerId
        assert currentVersion['elicitationMethod']['id'] == elicitationMethodId
        assert currentVersion['syntacticCategory']['id'] == lastSyntacticCategoryId
        assert currentVersion['verifier'] == None
        assert sorted([t['id'] for t in currentVersion['tags']]) == sorted(tagIds)
        assert sorted([f['id'] for f in currentVersion['files']]) == sorted(fileIds)
        assert len(currentVersion['morphemeBreakIDs']) == 4

        # Attempt to get the history of the just-entered restricted form as a
        # viewer and expect to fail with 403.
        extra_environ_viewer = {'test.authentication.role': u'viewer',
                         'test.applicationSettings': True}
        response = self.app.get(
            url(controller='forms', action='history', id=formId),
            headers=self.json_headers, extra_environ=extra_environ_viewer,
            status=403)
        resp = json.loads(response.body)
        assert response.content_type == 'application/json'
        assert resp['error'] == u'You are not authorized to access this resource.'

        # Attempt to call history with an invalid id and an invalid UUID and
        # expect 404 errors in both cases.
        badId = 103
        badUUID = str(uuid4())
        response = self.app.get(
            url(controller='forms', action='history', id=badId),
            headers=self.json_headers, extra_environ=extra_environ,
            status=404)
        resp = json.loads(response.body)
        assert resp['error'] == u'No forms or form backups match %d' % badId
        response = self.app.get(
            url(controller='forms', action='history', id=badUUID),
            headers=self.json_headers, extra_environ=extra_environ,
            status=404)
        resp = json.loads(response.body)
        assert resp['error'] == u'No forms or form backups match %s' % badUUID

        # Now delete the form ...
        response = self.app.delete(url('form', id=formId),
                        headers=self.json_headers, extra_environ=extra_environ)

        # ... and get its history again, this time using the form's UUID
        response = self.app.get(
            url(controller='forms', action='history', id=formUUID),
            headers=self.json_headers, extra_environ=extra_environ)
        byUUIDResp = json.loads(response.body)
        assert byUUIDResp['form'] == None
        assert len(byUUIDResp['previousVersions']) == 3
        firstVersion = byUUIDResp['previousVersions'][2]
        secondVersion = byUUIDResp['previousVersions'][1]
        thirdVersion = byUUIDResp['previousVersions'][0]
        assert firstVersion['transcription'] == u'created by the contributor'
        assert firstVersion['morphemeBreak'] == u''
        assert firstVersion['elicitor']['id'] == contributorId
        assert firstVersion['enterer']['id'] == contributorId
        assert firstVersion['backuper']['id'] == administratorId
        # Should be <; however, MySQL<5.6.4 does not support microseconds in datetimes 
        # so the test will fail/be inconsistent with <
        assert firstVersion['datetimeModified'] <= secondVersion['datetimeModified']
        assert firstVersion['speaker'] == None
        assert firstVersion['elicitationMethod'] == None
        assert firstVersion['syntacticCategory'] == None
        assert firstVersion['verifier'] == None
        assert [t['id'] for t in firstVersion['tags']] == [restrictedTagId]
        assert firstVersion['files'] == []
        assert firstVersion['morphemeBreakIDs'] == None

        assert secondVersion['transcription'] == u'updated by the administrator'
        assert secondVersion['morphemeBreak'] == u'up-dat-ed by the ad-ministr-ator'
        assert secondVersion['elicitor'] == None
        assert secondVersion['enterer']['id'] == contributorId
        assert secondVersion['backuper']['id'] == contributorId
        # Should be <; however, MySQL<5.6.4 does not support microseconds in datetimes 
        # so the test will fail/be inconsistent with <
        assert secondVersion['datetimeModified'] <= thirdVersion['datetimeModified']
        assert secondVersion['speaker']['id'] == speakerId
        assert secondVersion['elicitationMethod']['id'] == elicitationMethodId
        assert secondVersion['syntacticCategory']['id'] == firstSyntacticCategoryId
        assert secondVersion['verifier']['id'] == administratorId
        assert sorted([t['id'] for t in secondVersion['tags']]) == sorted(tagIds)
        assert secondVersion['files'] == []
        assert len(secondVersion['morphemeBreakIDs']) == 4

        assert thirdVersion['transcription'] == u'updated by the contributor'
        assert thirdVersion['morphemeBreak'] == u'up-dat-ed by the ad-ministr-ator'
        assert thirdVersion['elicitor'] == None
        assert thirdVersion['enterer']['id'] == contributorId
        assert 'backuper' in thirdVersion
        assert thirdVersion['speaker']['id'] == speakerId
        assert thirdVersion['elicitationMethod']['id'] == elicitationMethodId
        assert thirdVersion['syntacticCategory']['id'] == lastSyntacticCategoryId
        assert thirdVersion['verifier'] == None
        assert sorted([t['id'] for t in thirdVersion['tags']]) == sorted(tagIds)
        assert sorted([f['id'] for f in thirdVersion['files']]) == sorted(fileIds)
        assert len(thirdVersion['morphemeBreakIDs']) == 4

        # Get the deleted form's history again, this time using its id.  The 
        # response should be the same as the response received using the UUID.
        response = self.app.get(
            url(controller='forms', action='history', id=formId),
            headers=self.json_headers, extra_environ=extra_environ)
        byFormIdResp = json.loads(response.body)
        assert byFormIdResp == byUUIDResp

        # Create a new restricted form as an administrator.
        params = self.createParams.copy()
        params.update({
            'transcription': u'2nd form restricted',
            'translations': [{'transcription': u'2nd form restricted',
                         'grammaticality': u''}],
            'tags': [restrictedTagId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                        self.extra_environ_admin)
        resp = json.loads(response.body)
        formCount = Session.query(model.Form).count()
        formId = resp['id']
        formUUID = resp['UUID']
        assert formCount == 1

        # Update the just-created form by removing the restricted tag.
        params = self.createParams.copy()
        params.update({
            'transcription': u'2nd form unrestricted',
            'translations': [{'transcription': u'2nd form unrestricted', 'grammaticality': u''}],
            'tags': []
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=formId), params,
                        self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)

        # Now update it in another way.
        params = self.createParams.copy()
        params.update({
            'transcription': u'2nd form unrestricted updated',
            'translations': [{'transcription': u'2nd form unrestricted updated',
                         'grammaticality': u''}],
            'tags': []
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=formId), params,
                        self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)

        # Get the history of the just-entered restricted form as a
        # contributor and expect to receive only the '2nd form' version in the
        # previousVersions.
        response = self.app.get(
            url(controller='forms', action='history', id=formId),
            headers=self.json_headers, extra_environ=extra_environ)
        resp = json.loads(response.body)
        assert len(resp['previousVersions']) == 1
        assert resp['previousVersions'][0]['transcription'] == \
            u'2nd form unrestricted'
        assert resp['form']['transcription'] == u'2nd form unrestricted updated'

        # Now get the history of the just-entered restricted form as an
        # administrator and expect to receive both backups.
        response = self.app.get(
            url(controller='forms', action='history', id=formId),
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert len(resp['previousVersions']) == 2
        assert resp['previousVersions'][0]['transcription'] == \
            u'2nd form unrestricted'
        assert resp['previousVersions'][1]['transcription'] == \
            u'2nd form restricted'
        assert resp['form']['transcription'] == u'2nd form unrestricted updated'

    #@nottest
    def test_remember(self):
        """Tests that POST /forms/remember correctly saves the input list of forms to the logged in user's rememberedForms list.
        """
        # First create three forms, and restrict the first one.
        restrictedTag = h.generateRestrictedTag()
        form1 = h.generateDefaultForm()
        form2 = h.generateDefaultForm()
        form3 = h.generateDefaultForm()
        form1.transcription = u'form1'
        form2.transcription = u'form2'
        form3.transcription = u'form3'
        Session.add_all([form1, form2, form3, restrictedTag])
        Session.commit()
        restrictedTag = h.getRestrictedTag()
        form1.tags = [restrictedTag]
        Session.add(form1)
        Session.commit()
        forms = h.getForms()
        formIds = [form.id for form in forms]
        form1Id = [f.id for f in forms if f.transcription == u'form1'][0]
        formIdsSet = set(formIds)

        # Then try to remember all of these forms.  Send a JSON array of form
        # ids to remember and expect to get it back.
        administrator = Session.query(model.User).filter(model.User.role==u'administrator').first()
        administratorDatetimeModified = administrator.datetimeModified
        sleep(1)
        params = json.dumps({'forms': formIds})
        response = self.app.post(url(controller='forms', action='remember'),
            params, headers=self.json_headers,
            extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        administrator = Session.query(model.User).filter(model.User.role==u'administrator').first()
        assert response.content_type == 'application/json'
        assert len(resp) == len(formIds)
        assert formIdsSet == set(resp)
        assert administrator.datetimeModified != administratorDatetimeModified
        assert formIdsSet == set([f.id for f in administrator.rememberedForms])

        # A non-int-able form id in the input will result in a 400 error.
        badParams = formIds[:]
        badParams.append('a')
        badParams = json.dumps({'forms': badParams})
        response = self.app.post(url(controller='forms', action='remember'),
            badParams, headers=self.json_headers,
            extra_environ=self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        assert u'Please enter an integer value' in resp['errors']['forms']

        # One nonexistent form id will return a 400 error.
        badId = 1000
        badParams = formIds[:]
        badParams.append(badId)
        badParams = json.dumps({'forms': badParams})
        response = self.app.post(url(controller='forms', action='remember'),
            badParams, headers=self.json_headers,
            extra_environ=self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        assert u'There is no form with id %d.' % badId in resp['errors']['forms']

        # Bad JSON parameters will return its own 400 error.
        badJSON = u'[%d, %d, %d' % tuple(formIds)
        response = self.app.post(url(controller='forms', action='remember'),
            badJSON, headers=self.json_headers,
            extra_environ=self.extra_environ_admin, status=400)
        resp = json.loads(response.body)
        assert resp['error'] == \
            u'JSON decode error: the parameters provided were not valid JSON.'

        # An empty list ...
        emptyList = json.dumps([])
        response = self.app.post(url(controller='forms', action='remember'),
            emptyList, headers=self.json_headers,
            extra_environ=self.extra_environ_admin, status=404)
        resp = json.loads(response.body)
        assert resp['error'] == u'No valid form ids were provided.'

        # Re-issue the same remember request that succeeded previously.  Expect
        # user.rememberedForms to be unchanged (i.e., auto-duplicate removal)
        params = json.dumps({'forms': formIds})
        response = self.app.post(url(controller='forms', action='remember'),
            params, headers=self.json_headers,
            extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert len(resp) == len(formIds)
        assert formIdsSet == set(resp)
        administrator = Session.query(model.User).filter(
            model.User.role==u'administrator').first()
        assert formIdsSet == set([f.id for f in administrator.rememberedForms])
        userForms = Session.query(model.UserForm).filter(
            model.UserForm.user_id==administrator.id).all()
        assert len(userForms) == len(formIds)

        # Now again issue the same remember request that succeeded previously
        # but this time as a restricted user, a viewer.  Expect only 2 forms
        # returned.
        extra_environ_viewer = {'test.authentication.role': u'viewer'}
        params = json.dumps({'forms': formIds})
        response = self.app.post(url(controller='forms', action='remember'),
            params, headers=self.json_headers,
            extra_environ=extra_environ_viewer)
        resp = json.loads(response.body)
        assert len(resp) == len(formIds) - 1
        assert form1Id not in resp
        viewer = Session.query(model.User).filter(
            model.User.role==u'viewer').first()
        assert len(resp) == len(viewer.rememberedForms)
        assert form1Id not in [f.id for id in viewer.rememberedForms]

        # Finally, request to remember only the restricted form as a viewer.
        # Expect a 403 error.
        params = json.dumps({'forms': [form1Id]})
        response = self.app.post(url(controller='forms', action='remember'),
            params, headers=self.json_headers,
            extra_environ=extra_environ_viewer, status=403)
        resp = json.loads(response.body)
        assert resp['error'] == u'You are not authorized to access this resource.'
        viewer = Session.query(model.User).filter(
            model.User.role==u'viewer').first()
        assert len(viewer.rememberedForms) == 2
        assert form1Id not in [f.id for id in viewer.rememberedForms]

    #@nottest
    def _test_update_morpheme_references(self):
        """Tests that GET /forms/update_morpheme_references correctly updates the morpheme references.
        
        *NOTE*: this test has been deactivated (by prefixation with '_') because
        the update_morpheme_references functionality has been made obsolete by
        the calls to updateFormsContainingThisFormAsMorpheme in the create, update
        and delete actions.  If reactivated, this test will fail as is.
        """

        # First create a couple of syntactic categories and the application settings
        N = h.generateNSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        applicationSettings = h.generateDefaultApplicationSettings()
        Session.add_all([N, Num, applicationSettings])
        Session.commit()
        NId = N.id
        NumId = Num.id

        extra_environ = {'test.authentication.role': u'administrator',
                               'test.applicationSettings': True}

        # Create two forms with morphological analyses.
        params = self.createParams.copy()
        params.update({
            'transcription': u'abc',
            'morphemeBreak': u'a-b-c',
            'morphemeGloss': u'1-2-3',
            'translations': [{'transcription': u'123', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)
        params = self.createParams.copy()
        params.update({
            'transcription': u'xyz',
            'morphemeBreak': u'x-y-z',
            'morphemeGloss': u'7-8-9',
            'translations': [{'transcription': u'789', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        # GET the forms and confirm that the morphemeBreakIDs values are "empty"
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert len(resp) == 2
        assert [f['morphemeBreakIDs'] for f in resp] == [[[[], [], []]], [[[], [], []]]]
        assert [f['morphemeGlossIDs'] for f in resp] == [[[[], [], []]], [[[], [], []]]]
        assert [f['syntacticCategoryString'] for f in resp] == [u'?-?-?', u'?-?-?']

        # Request PUT /forms/update_morpheme_references and expect nothing to change
        response = self.app.put(url('/forms/update_morpheme_references'),
            headers=self.json_headers, extra_environ=self.extra_environ_admin)
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=extra_environ)
        resp2 = json.loads(response.body)
        assert [(f['id'], f['datetimeModified']) for f in resp] == \
            [(f['id'], f['datetimeModified']) for f in resp2]
        assert [f['morphemeBreakIDs'] for f in resp2] == [[[[], [], []]], [[[], [], []]]]
        assert [f['morphemeGlossIDs'] for f in resp2] == [[[[], [], []]], [[[], [], []]]]
        assert [f['syntacticCategoryString'] for f in resp2] == [u'?-?-?', u'?-?-?']

        # Now add the implicit lexical items for the two forms just entered and
        # *then* call /forms/update_morpheme_references and expect a change
        params = self.createParams.copy()
        params.update({
            'transcription': u'x',
            'morphemeBreak': u'x',
            'morphemeGloss': u'7',
            'translations': [{'transcription': u'7', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        params = self.createParams.copy()
        params.update({
            'transcription': u'y',
            'morphemeBreak': u'y',
            'morphemeGloss': u'8',
            'translations': [{'transcription': u'8', 'grammaticality': u''}],
            'syntacticCategory': NId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        params = self.createParams.copy()
        params.update({
            'transcription': u'z',
            'morphemeBreak': u'z',
            'morphemeGloss': u'9',
            'translations': [{'transcription': u'9', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        params = self.createParams.copy()
        params.update({
            'transcription': u'a',
            'morphemeBreak': u'a',
            'morphemeGloss': u'1',
            'translations': [{'transcription': u'1', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        params = self.createParams.copy()
        params.update({
            'transcription': u'b',
            'morphemeBreak': u'b',
            'morphemeGloss': u'2',
            'translations': [{'transcription': u'2', 'grammaticality': u''}],
            'syntacticCategory': NId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        params = self.createParams.copy()
        params.update({
            'transcription': u'c',
            'morphemeBreak': u'c',
            'morphemeGloss': u'3',
            'translations': [{'transcription': u'3', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers,
                                 extra_environ)

        # Request PUT /forms/update_morpheme_references
        sleep(1)
        response = self.app.put(url('/forms/update_morpheme_references'),
            headers=self.json_headers, extra_environ=extra_environ)
        assert response.content_type == 'application/json'

        # Search for our two original morphologically complex forms
        jsonQuery = json.dumps({'query': {'filter':
            ['Form', 'id', 'in', [f['id'] for f in resp]]}})
        response = self.app.post(url('/forms/search'), jsonQuery,
                        self.json_headers, self.extra_environ_admin)

        resp3 = json.loads(response.body)
        assert [f['id'] for f in resp] == [f['id'] for f in resp2] == [f['id'] for f in resp3]
        assert [f['datetimeModified'] for f in resp3] != [f['datetimeModified'] for f in resp2]
        assert [f['datetimeModified'] for f in resp3] != [f['datetimeModified'] for f in resp]

        assert resp3[0]['morphemeBreakIDs'][0][0][0][1] == u'1'
        assert resp3[0]['morphemeBreakIDs'][0][0][0][2] == u'Num'
        assert resp3[0]['morphemeBreakIDs'][0][1][0][1] == u'2'
        assert resp3[0]['morphemeBreakIDs'][0][1][0][2] == u'N'
        assert resp3[0]['morphemeBreakIDs'][0][2][0][1] == u'3'
        assert resp3[0]['morphemeBreakIDs'][0][2][0][2] == u'Num'
        assert resp3[0]['morphemeGlossIDs'][0][0][0][1] == u'a'
        assert resp3[0]['morphemeGlossIDs'][0][0][0][2] == u'Num'
        assert resp3[0]['morphemeGlossIDs'][0][1][0][1] == u'b'
        assert resp3[0]['morphemeGlossIDs'][0][1][0][2] == u'N'
        assert resp3[0]['morphemeGlossIDs'][0][2][0][1] == u'c'
        assert resp3[0]['morphemeGlossIDs'][0][2][0][2] == u'Num'

        assert resp3[0]['syntacticCategoryString'] == u'Num-N-Num'

        assert resp3[1]['morphemeBreakIDs'][0][0][0][1] == u'7'
        assert resp3[1]['morphemeBreakIDs'][0][0][0][2] == u'Num'
        assert resp3[1]['morphemeBreakIDs'][0][1][0][1] == u'8'
        assert resp3[1]['morphemeBreakIDs'][0][1][0][2] == u'N'
        assert resp3[1]['morphemeBreakIDs'][0][2][0][1] == u'9'
        assert resp3[1]['morphemeBreakIDs'][0][2][0][2] == u'Num'

        assert resp3[1]['morphemeGlossIDs'][0][0][0][1] == u'x'
        assert resp3[1]['morphemeGlossIDs'][0][0][0][2] == u'Num'
        assert resp3[1]['morphemeGlossIDs'][0][1][0][1] == u'y'
        assert resp3[1]['morphemeGlossIDs'][0][1][0][2] == u'N'
        assert resp3[1]['morphemeGlossIDs'][0][2][0][1] == u'z'
        assert resp3[1]['morphemeGlossIDs'][0][2][0][2] == u'Num'

        assert resp3[1]['syntacticCategoryString'] == u'Num-N-Num'

        formBackups = Session.query(model.FormBackup).all()
        assert len(formBackups) == 2
        assert [json.loads(f.morphemeBreakIDs) for f in formBackups] == \
            [[[[], [], []]], [[[], [], []]]]
        assert [json.loads(f.backuper)['role'] for f in formBackups] == [
            u'administrator', u'administrator']

    #@nottest
    def test_new_search(self):
        """Tests that GET /forms/new_search returns the search parameters for searching the forms resource."""
        queryBuilder = SQLAQueryBuilder('Form')
        response = self.app.get(url('/forms/new_search'), headers=self.json_headers,
                                extra_environ=self.extra_environ_view)
        resp = json.loads(response.body)
        assert resp['searchParameters'] == h.getSearchParameters(queryBuilder)

    #@nottest
    def test_create_restricted(self):
        """Tests what happens when a restricted user restricts a form.

        This should be possible since restricted users are able to access the
        restricted forms IF they are the enterer.
        """

        users = h.getUsers()
        contributor = [u for u in users if u.role == u'contributor'][0]
        contributorId = contributor.id
        administrator = [u for u in users if u.role == u'administrator'][0]
        administratorId = administrator.id
        restrictedTag = h.generateRestrictedTag()
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.unrestrictedUsers = []
        Session.add_all([applicationSettings, restrictedTag])
        Session.commit()
        restrictedTagId = restrictedTag.id

        # Create a restricted form as a restricted user (the contributor).
        extra_environ = {'test.authentication.id': contributorId,
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'transcription': u'test restricted tag transcription',
            'translations': [{'transcription': u'test restricted tag translation',
                         'grammaticality': u''}],
            'tags': [restrictedTagId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        restrictedFormId = resp['id']
        assert u'restricted' in [t['name'] for t in resp['tags']]

        # Create a restricted form as an unrestricted user (administrator).
        extra_environ = {'test.authentication.id': administratorId,
                         'test.applicationSettings': True}
        params = self.createParams.copy()
        params.update({
            'transcription': u'test restricted tag transcription',
            'translations': [{'transcription': u'test restricted tag translation',
                         'grammaticality': u''}],
            'tags': [restrictedTagId]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        restrictedFormId = resp['id']
        assert u'restricted' in [t['name'] for t in resp['tags']]

        # Try to get the restricted tag as the viewer and expect to fail
        extra_environ = {'test.authentication.id': contributorId,
                         'test.applicationSettings': True}
        response = self.app.get(url('form', id=restrictedFormId), headers=self.json_headers,
                                extra_environ=extra_environ, status=403)
        resp = json.loads(response.body)
        assert resp['error'] == u'You are not authorized to access this resource.'

    #@nottest
    def test_normalization(self):
        """Tests that unicode input data are normalized and so too are search patterns."""

        addSEARCHToWebTestValidMethods()
        eAcuteCombining = u'e\u0301'  # LATIN SMALL LETTER E, COMBINING ACUTE ACCENT
        eAcutePrecomposed = u'\u00E9'   # LATIN SMALL LETTER E WITH ACUTE

        # Create a form with a unicode combining character in its transcription
        params = self.createParams.copy()
        params.update({
            'transcription': eAcuteCombining,
            'translations': [{'transcription': u'test normalization', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        combiningFormId = resp['id']
        combiningTranscription = resp['transcription']

        # Create a form with a unicode precomposed character in its transcription
        params = self.createParams.copy()
        params.update({
            'transcription': eAcutePrecomposed,
            'translations': [{'transcription': u'test normalization', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, self.extra_environ_admin)
        resp = json.loads(response.body)
        precomposedFormId = resp['id']
        precomposedTranscription = resp['transcription']
        assert combiningTranscription == precomposedTranscription   # h.normalize converts these both to u'e\u0301'

        # Now search for the precomposed character and expect to find two matches
        jsonQuery = json.dumps(
            {'query': {'filter': ['Form', 'transcription', 'like', u'%\u00E9%']}})
        response = self.app.request(url('forms'), method='SEARCH',
            body=jsonQuery, headers=self.json_headers, environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert len(resp) == 2
        assert sorted([f['id'] for f in resp]) == sorted([combiningFormId, precomposedFormId])

        # Search for the e + combining accute and expect to find the same two matches
        jsonQuery = json.dumps(
            {'query': {'filter': ['Form', 'transcription', 'like', u'%e\u0301%']}})
        response = self.app.request(url('forms'), method='SEARCH',
            body=jsonQuery, headers=self.json_headers, environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        assert len(resp) == 2
        assert sorted([f['id'] for f in resp]) == sorted([combiningFormId, precomposedFormId])


    #@nottest
    def test_lexical_percolation(self):
        """Tests that creation, updating and deletion of a lexical forms percolates up to the phrasal forms containing them.
        """

        # First create a couple of syntactic categories and the application settings
        Agr = model.SyntacticCategory()
        Agr.name = u'Agr'
        N = h.generateNSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        applicationSettings = h.generateDefaultApplicationSettings()
        Session.add_all([N, Num, applicationSettings, Agr])
        Session.commit()
        NId = N.id
        NumId = Num.id
        AgrId = Agr.id

        extra_environ = {'test.authentication.role': u'administrator',
                               'test.applicationSettings': True}

        # Create two forms with morphological analyses.
        params = self.createParams.copy()
        params.update({
            'transcription': u'abc',
            'morphemeBreak': u'a-b-c',
            'morphemeGloss': u'1-2-3',
            'translations': [{'transcription': u'123', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        abcId = json.loads(response.body)['id']

        params = self.createParams.copy()
        params.update({
            'transcription': u'xyz',
            'morphemeBreak': u'x-y-z',
            'morphemeGloss': u'7-8-9',
            'translations': [{'transcription': u'789', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        xyzId = json.loads(response.body)['id']

        # GET the forms and confirm that the morphemeBreakIDs values are "empty"
        response = self.app.get(url('forms'), headers=self.json_headers,
                                extra_environ=self.extra_environ_admin)
        resp = json.loads(response.body)
        phrasalIds = [f['id'] for f in resp]
        assert len(resp) == 2
        assert [f['morphemeBreakIDs'] for f in resp] == [[[[], [], []]], [[[], [], []]]]
        assert [f['morphemeGlossIDs'] for f in resp] == [[[[], [], []]], [[[], [], []]]]
        assert [f['syntacticCategoryString'] for f in resp] == [u'?-?-?', u'?-?-?']

        # Now add the implicit lexical items for the two forms just entered and
        # expect the morphemeBreakIDs (etc.) fields of the two phrasal forms to
        # have changed.
        sleep(1)

        xParams = self.createParams.copy()
        xParams.update({
            'transcription': u'x',
            'morphemeBreak': u'x',
            'morphemeGloss': u'7',
            'translations': [{'transcription': u'7', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        xParams = json.dumps(xParams)
        response = self.app.post(url('forms'), xParams, self.json_headers, extra_environ)
        xResp = json.loads(response.body)
        xId = xResp['id']
        assert xResp['morphemeBreakIDs'][0][0][0][1] == u'7'
        assert xResp['morphemeBreakIDs'][0][0][0][2] == u'Num'
        assert xResp['morphemeGlossIDs'][0][0][0][1] == u'x'
        assert xResp['morphemeGlossIDs'][0][0][0][2] == u'Num'
        assert xResp['syntacticCategoryString'] == u'Num'
        assert xResp['breakGlossCategory'] == u'x|7|Num'

        yParams = self.createParams.copy()
        yParams.update({
            'transcription': u'y',
            'morphemeBreak': u'y',
            'morphemeGloss': u'8',
            'translations': [{'transcription': u'8', 'grammaticality': u''}],
            'syntacticCategory': NId
        })
        yParams = json.dumps(yParams)
        response = self.app.post(url('forms'), yParams, self.json_headers, extra_environ)
        yId = json.loads(response.body)['id']

        zParams = self.createParams.copy()
        zParams.update({
            'transcription': u'z',
            'morphemeBreak': u'z',
            'morphemeGloss': u'9',
            'translations': [{'transcription': u'9', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        zParams = json.dumps(zParams)
        response = self.app.post(url('forms'), zParams, self.json_headers, extra_environ)
        zId = json.loads(response.body)['id']

        aParams = self.createParams.copy()
        aParams.update({
            'transcription': u'a',
            'morphemeBreak': u'a',
            'morphemeGloss': u'1',
            'translations': [{'transcription': u'1', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        aParams = json.dumps(aParams)
        response = self.app.post(url('forms'), aParams, self.json_headers, extra_environ)
        aId = json.loads(response.body)['id']

        bParams = self.createParams.copy()
        bParams.update({
            'transcription': u'b',
            'morphemeBreak': u'b',
            'morphemeGloss': u'2',
            'translations': [{'transcription': u'2', 'grammaticality': u''}],
            'syntacticCategory': NId
        })
        bParams = json.dumps(bParams)
        response = self.app.post(url('forms'), bParams, self.json_headers, extra_environ)
        bId = json.loads(response.body)['id']

        cParams = self.createParams.copy()
        cParams.update({
            'transcription': u'c',
            'morphemeBreak': u'c',
            'morphemeGloss': u'3',
            'translations': [{'transcription': u'3', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        cParams = json.dumps(cParams)
        response = self.app.post(url('forms'), cParams, self.json_headers, extra_environ)
        cId = json.loads(response.body)['id']

        # Use search to get our two original morphologically complex forms
        jsonQuery = json.dumps({'query': {'filter':
            ['Form', 'id', 'in', phrasalIds]}})
        response = self.app.post(url('/forms/search'), jsonQuery,
                        self.json_headers, self.extra_environ_admin)

        resp2 = json.loads(response.body)
        assert [f['id'] for f in resp] == [f['id'] for f in resp2]
        assert [f['datetimeModified'] for f in resp2] != [f['datetimeModified'] for f in resp]

        assert resp2[0]['morphemeBreakIDs'][0][0][0][1] == u'1'
        assert resp2[0]['morphemeBreakIDs'][0][0][0][2] == u'Num'
        assert resp2[0]['morphemeBreakIDs'][0][1][0][1] == u'2'
        assert resp2[0]['morphemeBreakIDs'][0][1][0][2] == u'N'
        assert resp2[0]['morphemeBreakIDs'][0][2][0][1] == u'3'
        assert resp2[0]['morphemeBreakIDs'][0][2][0][2] == u'Num'

        assert resp2[0]['morphemeGlossIDs'][0][0][0][1] == u'a'
        assert resp2[0]['morphemeGlossIDs'][0][0][0][2] == u'Num'
        assert resp2[0]['morphemeGlossIDs'][0][1][0][1] == u'b'
        assert resp2[0]['morphemeGlossIDs'][0][1][0][2] == u'N'
        assert resp2[0]['morphemeGlossIDs'][0][2][0][1] == u'c'
        assert resp2[0]['morphemeGlossIDs'][0][2][0][2] == u'Num'

        assert resp2[0]['syntacticCategoryString'] == u'Num-N-Num'
        assert resp2[0]['breakGlossCategory'] == u'a|1|Num-b|2|N-c|3|Num'

        assert resp2[1]['morphemeBreakIDs'][0][0][0][1] == u'7'
        assert resp2[1]['morphemeBreakIDs'][0][0][0][2] == u'Num'
        assert resp2[1]['morphemeBreakIDs'][0][1][0][1] == u'8'
        assert resp2[1]['morphemeBreakIDs'][0][1][0][2] == u'N'
        assert resp2[1]['morphemeBreakIDs'][0][2][0][1] == u'9'
        assert resp2[1]['morphemeBreakIDs'][0][2][0][2] == u'Num'

        assert resp2[1]['morphemeGlossIDs'][0][0][0][1] == u'x'
        assert resp2[1]['morphemeGlossIDs'][0][0][0][2] == u'Num'
        assert resp2[1]['morphemeGlossIDs'][0][1][0][1] == u'y'
        assert resp2[1]['morphemeGlossIDs'][0][1][0][2] == u'N'
        assert resp2[1]['morphemeGlossIDs'][0][2][0][1] == u'z'
        assert resp2[1]['morphemeGlossIDs'][0][2][0][2] == u'Num'

        assert resp2[1]['syntacticCategoryString'] == u'Num-N-Num'
        assert resp2[1]['breakGlossCategory'] == u'x|7|Num-y|8|N-z|9|Num'

        formBackups = Session.query(model.FormBackup).all()
        assert len(formBackups) == 6    # each lexical item creation updates one phrasal form

        # Now update the lexical items and expect updates in the phrasal ones too

        # Update the morphemeBreak value of the lexical form 'x' and expect the
        # phrasal form 'xyz' to get updated too.
        formBackupCount = Session.query(model.FormBackup).count()
        fbs = Session.query(model.FormBackup).order_by(model.FormBackup.id).all()
        xParams = json.loads(xParams)
        xParams['morphemeBreak'] = u'xx'
        xParams = json.dumps(xParams)
        response = self.app.put(url('form', id=xId), xParams, self.json_headers, extra_environ)
        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        newFormBackupCount = Session.query(model.FormBackup).count()
        fbs = Session.query(model.FormBackup).order_by(model.FormBackup.id).all()
        assert newFormBackupCount == formBackupCount + 2    # 'x' and 'xyz' are both updated
        assert xyzMorphemeGlossIDs[0][0][0][1] == u'xx' # The 'x' morpheme is still glossed as '7'
        assert xyzMorphemeBreakIDs[0][0] == []  # No more 'x' morpheme so w1, m1 is empty
        assert xyzPhrase.breakGlossCategory == u'x|7|Num-y|8|N-z|9|Num' # Stays unchanged
        assert xyzPhrase.syntacticCategoryString == u'Num-N-Num'      # " "

        # Update the morphemeGloss value of the lexical form 'y' and expect the
        # phrasal form 'xyz' to get updated too.
        yParams = json.loads(yParams)
        yParams['morphemeGloss'] = u'88'
        yParams = json.dumps(yParams)
        response = self.app.put(url('form', id=yId), yParams, self.json_headers, extra_environ)
        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormBackupCount == formBackupCount + 2
        assert xyzMorphemeBreakIDs[0][1][0][1] == u'88' # The 'y' morpheme is now glossed as '88'
        assert xyzMorphemeGlossIDs[0][1] == []  # No more '8' morpheme so w1, m1 is empty
        assert xyzPhrase.breakGlossCategory == u'x|7|Num-y|8|N-z|9|Num' # Stays unchanged
        assert xyzPhrase.syntacticCategoryString == u'Num-N-Num'      # " "

        # Update the syntactic category of the lexical form 'z' and expect the
        # phrasal form 'xyz' to get updated too.
        zParams = json.loads(zParams)
        zParams['syntacticCategory'] = NId
        zParams = json.dumps(zParams)
        response = self.app.put(url('form', id=zId), zParams, self.json_headers, extra_environ)
        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormBackupCount == formBackupCount + 2
        assert xyzMorphemeBreakIDs[0][2][0][2] == u'N' # The 'z' morpheme now has 'N' for category
        assert xyzMorphemeGlossIDs[0][2][0][2] == u'N' # redundant, I know
        assert xyzPhrase.breakGlossCategory == u'x|7|Num-y|8|N-z|9|N'
        assert xyzPhrase.syntacticCategoryString == u'Num-N-N'

        # Save these values for the next test:
        xyzPhraseMorphemeBreakIDs = xyzPhrase.morphemeBreakIDs
        xyzPhraseMorphemeGlossIDs = xyzPhrase.morphemeGlossIDs
        xyzPhraseBreakGlossCategory = xyzPhrase.breakGlossCategory
        xyzPhraseSyntacticCategoryString = xyzPhrase.syntacticCategoryString

        # Update the lexical form 'z' in a way that is irrelevant to the phrasal
        # form 'xyz'; expect 'xyz' to be unaffected.
        zParams = json.loads(zParams)
        zParams['transcription'] = u'zZz'
        zParams['translations'] = [{'transcription': u'999', 'grammaticality': u''}]
        zParams = json.dumps(zParams)
        response = self.app.put(url('form', id=zId), zParams, self.json_headers, extra_environ)
        newXyzPhrase = Session.query(model.Form).get(xyzId)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormBackupCount == formBackupCount + 1    # only the lexical item has been updated
        assert xyzPhraseMorphemeBreakIDs == newXyzPhrase.morphemeBreakIDs
        assert xyzPhraseMorphemeGlossIDs == newXyzPhrase.morphemeGlossIDs
        assert xyzPhraseBreakGlossCategory == newXyzPhrase.breakGlossCategory
        assert xyzPhraseSyntacticCategoryString == newXyzPhrase.syntacticCategoryString

        # Now create a new lexical item that will cause the 'xyz' phrasal form to be udpated
        x2Params = self.createParams.copy()
        x2Params.update({
            'transcription': u'x',
            'morphemeBreak': u'x',
            'morphemeGloss': u'7',
            'translations': [{'transcription': u'7', 'grammaticality': u''}],
            'syntacticCategory': AgrId
        })
        x2Params = json.dumps(x2Params)
        response = self.app.post(url('forms'), x2Params, self.json_headers, extra_environ)
        x2Id = json.loads(response.body)['id']

        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormBackupCount == formBackupCount + 1    # 'xyz' will have been updated
        assert xyzMorphemeGlossIDs[0][0][0][1] == u'x' # The new 'x' morpheme ousts the old ill-matching one
        assert xyzMorphemeBreakIDs[0][0][0][1] == u'7' # " "
        assert len(xyzMorphemeBreakIDs[0][0]) == 1  # The 'xx/7' partial match has been removed in favour of the 'x/7' perfect match
        assert xyzMorphemeBreakIDs[0][0][0][2] == u'Agr'
        assert xyzPhrase.breakGlossCategory == u'x|7|Agr-y|8|N-z|9|N'
        assert xyzPhrase.syntacticCategoryString == u'Agr-N-N'

        # Delete the 'y' morpheme and expect the 'xyz' phrase to be udpated.
        response = self.app.delete(url('form', id=yId), headers=self.json_headers,
                                   extra_environ=extra_environ)
        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormBackupCount == formBackupCount + 2    # 'xyz' and 'y' will both have been backed up
        assert xyzMorphemeGlossIDs[0][1] == []
        assert xyzMorphemeBreakIDs[0][1] == []
        assert xyzPhrase.breakGlossCategory == u'x|7|Agr-y|8|?-z|9|N'
        assert xyzPhrase.syntacticCategoryString == u'Agr-?-N'

        # Delete the 'x/7' morpheme and expect the 'xyz' phrase to be udpated.  The
        # partial match 'xx/7' morpheme will now again be referenced in xyzForm.morphemeGlossIDs
        response = self.app.delete(url('form', id=x2Id), headers=self.json_headers, extra_environ=extra_environ)
        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        assert newFormBackupCount == formBackupCount + 2    # 'xyz' and 'x' will both have been backed up
        assert xyzMorphemeGlossIDs[0][0][0][1] == u'xx'
        assert xyzMorphemeGlossIDs[0][0][0][2] == u'Num'
        assert xyzMorphemeBreakIDs[0][0] == []
        assert xyzPhrase.breakGlossCategory == u'x|7|Num-y|8|?-z|9|N'
        assert xyzPhrase.syntacticCategoryString == u'Num-?-N'

        # Update the lexical form 'z' so that its new morphemeBreak and morphemeGloss
        # values no longer match the 'xyz' phrasal form.  Expect the 'xyz' form
        # to be updated (shows that potentially affected forms are discovered by
        # searching for matches to the altered lexcical item's current *and* previous
        # states.)
        zParams = json.loads(zParams)
        zParams['morphemeBreak'] = u'm'
        zParams['morphemeGloss'] = u'4'
        zParams = json.dumps(zParams)
        response = self.app.put(url('form', id=zId), zParams, self.json_headers, extra_environ)
        newXyzPhrase = Session.query(model.Form).get(xyzId)
        formBackupCount = newFormBackupCount
        newFormBackupCount = Session.query(model.FormBackup).count()
        xyzPhrase = Session.query(model.Form).get(xyzId)
        xyzMorphemeGlossIDs = json.loads(xyzPhrase.morphemeGlossIDs)
        xyzMorphemeBreakIDs = json.loads(xyzPhrase.morphemeBreakIDs)
        assert newFormBackupCount == formBackupCount + 2    # only the lexical item has been updated
        assert xyzMorphemeBreakIDs[0][2] == []
        assert xyzMorphemeGlossIDs[0][2] == []
        assert xyzPhrase.breakGlossCategory == u'x|7|Num-y|8|?-z|9|?'
        assert xyzPhrase.syntacticCategoryString == u'Num-?-?'

        # Update the xyz form so that the delimiters used in the morphemeBreak
        # and morphemeGloss lines do not match.  Show that the morpheme
        # delimiters from the morphemeBreak line are the ones that are used in
        # the breakGlossCategory and syntacticCategoryString values.
        params = self.createParams.copy()
        params.update({
            'transcription': u'xyz',
            'morphemeBreak': u'x=y-z',
            'morphemeGloss': u'7-8=9',
            'translations': [{'transcription': u'789', 'grammaticality': u''}]
        })
        params = json.dumps(params)
        response = self.app.put(url('form', id=xyzId), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        assert resp['syntacticCategoryString'] == u'Num=?-?'
        assert resp['morphemeGlossIDs'] == xyzMorphemeGlossIDs
        assert resp['breakGlossCategory'] == u'x|7|Num=y|8|?-z|9|?'

    #@nottest
    def test_morphemic_analysis_compilation(self):
        """Tests the behaviour of compileMorphemicAnalysis in the forms controller.

        In particular, tests:

        1. that regular expression metacharacters like the caret "^" can be used
           as morpheme delimiters and
        2. that compileMorphemicAnalysis works even when no morpheme delimiters
           are supplied and
        3. the matchesFound dict in compileMorphemicAnalysis reduces redundant
           db queries and processing.

        """

        # First create a couple of syntactic categories and the application settings
        T = model.SyntacticCategory()
        T.name = u'T'
        D = model.SyntacticCategory()
        D.name = u'D'
        Agr = model.SyntacticCategory()
        Agr.name = u'Agr'
        N = h.generateNSyntacticCategory()
        V = h.generateVSyntacticCategory()
        S = h.generateSSyntacticCategory()
        Num = h.generateNumSyntacticCategory()
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.morphemeDelimiters = u''    # NO MORPHEME DELIMITERS
        Session.add_all([N, V, D, T, Num, Agr, S, applicationSettings])
        Session.commit()
        TId = T.id
        DId = D.id
        NId = N.id
        VId = V.id
        SId = S.id
        NumId = Num.id
        AgrId = Agr.id

        extra_environ = {'test.authentication.role': u'administrator',
                               'test.applicationSettings': True}

        # Test that compileMorphemicAnalysis works when there are no morpheme delimiters

        # First add a sentence with no word-internal morphemes indicated
        params = self.createParams.copy()
        params.update({
            'transcription': u'Le chien a courru.',
            'morphemeBreak': u'le chien a courru',
            'morphemeGloss': u'the dog has run.PP',
            'translations': [{'transcription': u'The dog ran.', 'grammaticality': u''}],
            'syntacticCategory': SId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        sentId = resp['id']
        assert resp['morphemeBreakIDs'] == [[[]], [[]], [[]], [[]]]
        assert resp['syntacticCategoryString'] == u'? ? ? ?'
        assert resp['breakGlossCategory'] == u'le|the|? chien|dog|? a|has|? courru|run.PP|?'

        # Now add the words/morphemes for the sentence above.
        params = self.createParams.copy()
        params.update({
            'transcription': u'le',
            'morphemeBreak': u'le',
            'morphemeGloss': u'the',
            'translations': [{'transcription': u'the', 'grammaticality': u''}],
            'syntacticCategory': DId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        leId = resp['id']
        assert resp['morphemeBreakIDs'][0][0][0][1] == u'the'
        assert resp['morphemeBreakIDs'][0][0][0][2] == u'D'
        assert resp['morphemeGlossIDs'][0][0][0][1] == u'le'
        assert resp['syntacticCategoryString'] == u'D'
        assert resp['breakGlossCategory'] == u'le|the|D'

        params = self.createParams.copy()
        params.update({
            'transcription': u'chien',
            'morphemeBreak': u'chien',
            'morphemeGloss': u'dog',
            'translations': [{'transcription': u'dog', 'grammaticality': u''}],
            'syntacticCategory': NId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        chienId = resp['id']

        params = self.createParams.copy()
        params.update({
            'transcription': u'a',
            'morphemeBreak': u'a',
            'morphemeGloss': u'has',
            'translations': [{'transcription': u'has', 'grammaticality': u''}],
            'syntacticCategory': TId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        aId = resp['id']

        params = self.createParams.copy()
        params.update({
            'transcription': u'courru',
            'morphemeBreak': u'courru',
            'morphemeGloss': u'run.PP',
            'translations': [{'transcription': u'run', 'grammaticality': u''}],
            'syntacticCategory': VId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        courruId = resp['id']

        sentence = Session.query(model.Form).get(sentId)
        morphemeBreakIDs = json.loads(sentence.morphemeBreakIDs)
        morphemeGlossIDs = json.loads(sentence.morphemeGlossIDs)
        assert morphemeBreakIDs[0][0][0][1] == u'the'
        assert morphemeBreakIDs[0][0][0][2] == u'D'
        assert morphemeBreakIDs[1][0][0][1] == u'dog'
        assert morphemeBreakIDs[1][0][0][2] == u'N'
        assert morphemeBreakIDs[2][0][0][1] == u'has'
        assert morphemeBreakIDs[2][0][0][2] == u'T'
        assert morphemeBreakIDs[3][0][0][1] == u'run.PP'
        assert morphemeBreakIDs[3][0][0][2] == u'V'

        assert morphemeGlossIDs[0][0][0][1] == u'le'
        assert morphemeGlossIDs[0][0][0][2] == u'D'
        assert morphemeGlossIDs[1][0][0][1] == u'chien'
        assert morphemeGlossIDs[1][0][0][2] == u'N'
        assert morphemeGlossIDs[2][0][0][1] == u'a'
        assert morphemeGlossIDs[2][0][0][2] == u'T'
        assert morphemeGlossIDs[3][0][0][1] == u'courru'
        assert morphemeGlossIDs[3][0][0][2] == u'V'

        assert sentence.syntacticCategoryString == u'D N T V'
        assert sentence.breakGlossCategory == u'le|the|D chien|dog|N a|has|T courru|run.PP|V'

        # Ensure that regex metacharacters can be used as morpheme delimiters
        applicationSettings = h.generateDefaultApplicationSettings()
        applicationSettings.morphemeDelimiters = u'^,?,+,.'    # regexp metachars
        Session.add(applicationSettings)
        Session.commit()

        # Now add a sentence that is morphologically parsed using those odd delimiters
        params = self.createParams.copy()
        params.update({
            'transcription': u'Les chiens ont courru.',
            'morphemeBreak': u'le^s chien.s o?nt courr+u',
            'morphemeGloss': u'the^PL dog.PL have?3PL run+PP',
            'translations': [{'transcription': u'The dogs ran.', 'grammaticality': u''}],
            'syntacticCategory': SId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        sent2Id = resp['id']
        # Note that the only lexical items matching the above form are chien/dog and le/the
        assert resp['morphemeBreakIDs'][0][0][0][1] == u'the'
        assert resp['morphemeBreakIDs'][0][0][0][2] == u'D'
        assert resp['morphemeBreakIDs'][1][0][0][1] == u'dog'
        assert resp['morphemeBreakIDs'][1][0][0][2] == u'N'

        assert resp['morphemeGlossIDs'][0][0][0][1] == u'le'
        assert resp['morphemeGlossIDs'][0][0][0][2] == u'D'
        assert resp['morphemeGlossIDs'][1][0][0][1] == u'chien'
        assert resp['morphemeGlossIDs'][1][0][0][2] == u'N'

        assert resp['syntacticCategoryString'] == u'D^? N.? ??? ?+?'
        # The breakGlossCategory is ugly ... but it's what we should expect.
        assert resp['breakGlossCategory'] == u'le|the|D^s|PL|? chien|dog|N.s|PL|? o|have|??nt|3PL|? courr|run|?+u|PP|?'

        # s/PL/Num
        params = self.createParams.copy()
        params.update({
            'transcription': u's',
            'morphemeBreak': u's',
            'morphemeGloss': u'PL',
            'translations': [{'transcription': u'plural', 'grammaticality': u''}],
            'syntacticCategory': NumId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        sId = resp['id']

        # o/have/T
        params = self.createParams.copy()
        params.update({
            'transcription': u'o',
            'morphemeBreak': u'o',
            'morphemeGloss': u'have',
            'translations': [{'transcription': u'have', 'grammaticality': u''}],
            'syntacticCategory': TId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        oId = resp['id']

        # nt/3PL/Agr
        params = self.createParams.copy()
        params.update({
            'transcription': u'nt',
            'morphemeBreak': u'nt',
            'morphemeGloss': u'3PL',
            'translations': [{'transcription': u'third person plural', 'grammaticality': u''}],
            'syntacticCategory': AgrId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        ntId = resp['id']

        # courr/run/V
        params = self.createParams.copy()
        params.update({
            'transcription': u'courr',
            'morphemeBreak': u'courr',
            'morphemeGloss': u'run',
            'translations': [{'transcription': u'run', 'grammaticality': u''}],
            'syntacticCategory': VId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        courrId = resp['id']

        # u/PP/T
        params = self.createParams.copy()
        params.update({
            'transcription': u'u',
            'morphemeBreak': u'u',
            'morphemeGloss': u'PP',
            'translations': [{'transcription': u'past participle', 'grammaticality': u''}],
            'syntacticCategory': TId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
        resp = json.loads(response.body)
        uId = resp['id']

        sentence2 = Session.query(model.Form).get(sent2Id)
        morphemeBreakIDs = json.loads(sentence2.morphemeBreakIDs)
        morphemeGlossIDs = json.loads(sentence2.morphemeGlossIDs)

        assert morphemeBreakIDs[0][0][0][1] == u'the'
        assert morphemeBreakIDs[0][0][0][2] == u'D'
        assert morphemeBreakIDs[0][1][0][1] == u'PL'
        assert morphemeBreakIDs[0][1][0][2] == u'Num'

        assert morphemeBreakIDs[1][0][0][1] == u'dog'
        assert morphemeBreakIDs[1][0][0][2] == u'N'
        assert morphemeBreakIDs[1][1][0][1] == u'PL'
        assert morphemeBreakIDs[1][1][0][2] == u'Num'

        assert morphemeBreakIDs[2][0][0][1] == u'have'
        assert morphemeBreakIDs[2][0][0][2] == u'T'
        assert morphemeBreakIDs[2][1][0][1] == u'3PL'
        assert morphemeBreakIDs[2][1][0][2] == u'Agr'

        assert morphemeBreakIDs[3][0][0][1] == u'run'
        assert morphemeBreakIDs[3][0][0][2] == u'V'
        assert morphemeBreakIDs[3][1][0][1] == u'PP'
        assert morphemeBreakIDs[3][1][0][2] == u'T'

        assert morphemeGlossIDs[0][0][0][1] == u'le'
        assert morphemeGlossIDs[0][0][0][2] == u'D'
        assert morphemeGlossIDs[0][1][0][1] == u's'
        assert morphemeGlossIDs[0][1][0][2] == u'Num'

        assert morphemeGlossIDs[1][0][0][1] == u'chien'
        assert morphemeGlossIDs[1][0][0][2] == u'N'
        assert morphemeGlossIDs[1][1][0][1] == u's'
        assert morphemeGlossIDs[1][1][0][2] == u'Num'

        assert morphemeGlossIDs[2][0][0][1] == u'o'
        assert morphemeGlossIDs[2][0][0][2] == u'T'
        assert morphemeGlossIDs[2][1][0][1] == u'nt'
        assert morphemeGlossIDs[2][1][0][2] == u'Agr'

        assert morphemeGlossIDs[3][0][0][1] == u'courr'
        assert morphemeGlossIDs[3][0][0][2] == u'V'
        assert morphemeGlossIDs[3][1][0][1] == u'u'
        assert morphemeGlossIDs[3][1][0][2] == u'T'

        assert sentence2.syntacticCategoryString == u'D^Num N.Num T?Agr V+T'
        assert sentence2.breakGlossCategory == \
            u'le|the|D^s|PL|Num chien|dog|N.s|PL|Num o|have|T?nt|3PL|Agr courr|run|V+u|PP|T'

        # Now test that the matchesFound dict of compileMorphemicAnalysis reduces
        # redundant db requests & processing.  Note that seeing this requires
        # placing log.warn statements in the getPerfectMatches & getPartialMatches
        # sub-functions, e.g., log.warn('in getPerfectMatches and %s/%s was not queried!' % (morpheme, gloss))

        # Once matches for the first 7 unique morphemes of this form have been found,
        # compileMorphemicAnalysis should thenceforward rely on matchesFound for the
        # repeats.
        params = self.createParams.copy()
        params.update({
            'transcription': u'Les chiens ont courru; les chiens ont courru; les chiens ont courru.',
            'morphemeBreak': u'le^s chien.s o?nt courr+u le^s chien.s o?nt courr+u le^s chien.s o?nt courr+u',
            'morphemeGloss': u'the^PL dog.PL have?3PL run+PP the^PL dog.PL have?3PL run+PP the^PL dog.PL have?3PL run+PP',
            'translations': [{'transcription': u'The dogs ran; the dogs ran; the dogs ran.', 'grammaticality': u''}],
            'syntacticCategory': SId
        })
        params = json.dumps(params)
        response = self.app.post(url('forms'), params, self.json_headers, extra_environ)
