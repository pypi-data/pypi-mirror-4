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

import logging
import datetime
import re
import os, shutil
from cgi import FieldStorage
import simplejson as json
from string import letters, digits
from random import sample
from paste.fileapp import FileApp
from pylons import request, response, session, app_globals, config
from pylons.decorators.rest import restrict
from pylons.decorators import jsonify
from pylons.controllers.util import forward
from formencode.validators import Invalid
from sqlalchemy.exc import OperationalError, InvalidRequestError
from sqlalchemy.sql import asc
from sqlalchemy.orm import subqueryload
from onlinelinguisticdatabase.lib.base import BaseController
from onlinelinguisticdatabase.lib.schemata import FileCreateWithBase64EncodedFiledataSchema, \
    FileCreateWithFiledataSchema, FileSubintervalReferencingSchema, \
    FileExternallyHostedSchema, FileUpdateSchema
import onlinelinguisticdatabase.lib.helpers as h
from onlinelinguisticdatabase.lib.SQLAQueryBuilder import SQLAQueryBuilder, OLDSearchParseError
from onlinelinguisticdatabase.model.meta import Session, Model
from onlinelinguisticdatabase.model import File, User
from onlinelinguisticdatabase.lib.resize import saveReducedCopy

log = logging.getLogger(__name__)

class FilesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""

    queryBuilder = SQLAQueryBuilder('File', config=config)

    @h.jsonify
    @h.restrict('SEARCH', 'POST')
    @h.authenticate
    def search(self):
        """SEARCH /files: Return all files matching the filter passed as JSON in
        the request body.  Note: POST /files/search also routes to this action.
        The request body must be a JSON object with a 'query' attribute; a
        'paginator' attribute is optional.  The 'query' object is passed to the
        getSQLAQuery() method of an SQLAQueryBuilder instance and an SQLA query
        is returned or an error is raised.  The 'query' object requires a
        'filter' attribute; an 'orderBy' attribute is optional.
        """
        try:
            jsonSearchParams = unicode(request.body, request.charset)
            pythonSearchParams = json.loads(jsonSearchParams)
            SQLAQuery = h.eagerloadFile(
                self.queryBuilder.getSQLAQuery(pythonSearchParams.get('query')))
            query = h.filterRestrictedModels('File', SQLAQuery)
            return h.addPagination(query, pythonSearchParams.get('paginator'))
        except h.JSONDecodeError:
            response.status_int = 400
            return h.JSONDecodeErrorResponse
        except (OLDSearchParseError, Invalid), e:
            response.status_int = 400
            return {'errors': e.unpack_errors()}
        except:
            response.status_int = 400
            return {'error': u'The specified search parameters generated an invalid database query'}

    @h.jsonify
    @h.restrict('GET')
    @h.authenticate
    def new_search(self):
        """GET /files/new_search: Return the data necessary to inform a search
        on the files resource.
        """
        return {'searchParameters': h.getSearchParameters(self.queryBuilder)}

    @h.jsonify
    @h.restrict('GET')
    @h.authenticate
    def index(self):
        """GET /files: Return all files."""
        try:
            query = h.eagerloadFile(Session.query(File))
            query = h.addOrderBy(query, dict(request.GET), self.queryBuilder)
            query = h.filterRestrictedModels('File', query)
            return h.addPagination(query, dict(request.GET))
        except Invalid, e:
            response.status_int = 400
            return {'errors': e.unpack_errors()}

    @h.jsonify
    @h.restrict('POST')
    @h.authenticate
    @h.authorize(['administrator', 'contributor'])
    def create(self):
        """POST /files: Create a new file.  There are four ways to create a new
        file:

        1. Plain File:

           - Upload filedata via a POST request with Content-Type set to
             'multipart/form-data'.  A filename POST param should also be present.

        2. Base64-encoded File with JSON Metadata:

           - Upload the filedata (base64 encoded) and metadata all within a JSON
             POST request, i.e., Content-Type='application/json'.  This permits
             the uploading of everything in one go (all via JSON), the downside
             being the processing time required to encode to and decode from base64.

        3. Audio/Video Subinterval-Referencing File:

           - Upload file metadata in a JSON POST request and specify the id of an
             existing *audio/video* 'parentFile' as well as 'start' and 'end'
             attributes (in seconds as ints/floats) in the JSON request params.
             Here the name attribute is user-specifiable.

        4. Externally Hosted File:

           - JSON POST body of request must contain a url attribute; name,
             MIMEtype and password attributes are optional.
        """
        try:
            if request.content_type == 'application/json':
                if len(request.body) > 20971520:    # JSON/Base64 file upload caps out at ~20MB
                    response.status_int = 400
                    return {'error':
                        u'The request body is too large; use the multipart/form-data Content-Type when uploading files greater than 20MB.'}
                values = json.loads(unicode(request.body, request.charset))
                if 'base64EncodedFile' in values:
                    file = createBase64File(values)
                elif 'url' in values:
                    file = createExternallyHostedFile(values)
                else:
                    file = createSubintervalReferencingFile(values)
            else:
                file = createPlainFile()
            file.lossyFilename = saveReducedCopy(file, config)
            Session.add(file)
            Session.commit()
            return file
        except h.JSONDecodeError:
            response.status_int = 400
            return h.JSONDecodeErrorResponse
        except InvalidFieldStorageObjectError:
            response.status_int = 400
            return {'error': 'The attempted multipart/form-data file upload failed.'}
        except Invalid, e:
            response.status_int = 400
            return {'errors': e.unpack_errors()}

    @h.jsonify
    @h.restrict('GET')
    @h.authenticate
    @h.authorize(['administrator', 'contributor'])
    def new(self):
        """GET /new_file: Return the data necessary to create a new OLD file.

        Return a JSON object with the following properties: 'tags',
        'utteranceTypes', 'speakers' and 'users', the value of each of which is
        an array that is either empty or contains the appropriate objects.

        See the getNewEditFileData function to understand how the GET params can
        affect the contents of the arrays.
        """
        return getNewEditFileData(request.GET)

    @h.jsonify
    @h.restrict('PUT')
    @h.authenticate
    @h.authorize(['administrator', 'contributor'])
    def update(self, id):
        """PUT /files/id: Update an existing file."""
        file = h.eagerloadFile(Session.query(File)).get(int(id))
        if file:
            unrestrictedUsers = h.getUnrestrictedUsers()
            user = session['user']
            if h.userIsAuthorizedToAccessModel(user, file, unrestrictedUsers):
                try:
                    if getattr(file, 'parentFile', None):
                        file = updateSubintervalReferencingFile(file)
                    elif getattr(file, 'url', None):
                        file = updateExternallyHostedFile(file)
                    else:
                        file = updateFile(file)
                    # file will be False if there are no changes (cf. update(SubintervalReferencing)File).
                    if file:
                        Session.add(file)
                        Session.commit()
                        return file
                    else:
                        response.status_int = 400
                        return {'error':
                            u'The update request failed because the submitted data were not new.'}
                except h.JSONDecodeError:
                    response.status_int = 400
                    return h.JSONDecodeErrorResponse
                except Invalid, e:
                    response.status_int = 400
                    return {'errors': e.unpack_errors()}
            else:
                response.status_int = 403
                return h.unauthorizedMsg
        else:
            response.status_int = 404
            return {'error': 'There is no file with id %s' % id}

    @h.jsonify
    @h.restrict('DELETE')
    @h.authenticate
    @h.authorize(['administrator', 'contributor'])
    def delete(self, id):
        """DELETE /files/id: Delete an existing file.  Only the enterer and
        administrators can delete a file.
        """
        file = h.eagerloadFile(Session.query(File)).get(id)
        if file:
            if session['user'].role == u'administrator' or \
            file.enterer is session['user']:
                deleteFile(file)
                return file
            else:
                response.status_int = 403
                return h.unauthorizedMsg
        else:
            response.status_int = 404
            return {'error': 'There is no file with id %s' % id}

    @h.jsonify
    @h.restrict('GET')
    @h.authenticate
    def show(self, id):
        """GET /files/id: Return a JSON object representation of the file with
        id=id.

        If the id is invalid, the header will contain a 404 status int and a
        JSON object will be returned.  If the id is unspecified, then Routes
        will put a 404 status int into the header and the default 404 JSON
        object defined in controllers/error.py will be returned.
        """
        file = h.eagerloadFile(Session.query(File)).get(id)
        if file:
            unrestrictedUsers = h.getUnrestrictedUsers()
            user = session['user']
            if h.userIsAuthorizedToAccessModel(user, file, unrestrictedUsers):
                return file
            else:
                response.status_int = 403
                return h.unauthorizedMsg
        else:
            response.status_int = 404
            return {'error': 'There is no file with id %s' % id}

    @h.jsonify
    @h.restrict('GET')
    @h.authenticate
    @h.authorize(['administrator', 'contributor'])
    def edit(self, id):
        """GET /files/id/edit: Return the data necessary to update an existing
        OLD file, i.e., the file's properties and the necessary additional data,
        i.e., users, speakers, etc.

        This action can be thought of as a combination of the 'show' and 'new'
        actions.  The output will be a JSON object of the form

            {file: {...}, data: {...}},

        where output.file is an object containing the file's properties (cf. the
        output of show) and output.data is an object containing the data
        required to add a new file (cf. the output of new).

        GET parameters will affect the value of output.data in the same way as
        for the new action, i.e., no params will result in all the necessary
        output.data being retrieved from the db while specified params will
        result in selective retrieval (see getNewEditFileData for details).
        """
        response.content_type = 'application/json'
        file = h.eagerloadFile(Session.query(File)).get(id)
        if file:
            unrestrictedUsers = h.getUnrestrictedUsers()
            if h.userIsAuthorizedToAccessModel(session['user'], file, unrestrictedUsers):
                return {'data': getNewEditFileData(request.GET), 'file': file}
            else:
                response.status_int = 403
                return h.unauthorizedMsg
        else:
            response.status_int = 404
            return {'error': 'There is no file with id %s' % id}

    @h.restrict('GET')
    @h.authenticateWithJSON
    def serve(self, id):
        """Return the file data (binary stream) for the file in files/ with
        id=id or an error message if the file does not exist or the user is
        not authorized to access it.
        """
        return serveFile(id)

    @h.restrict('GET')
    @h.authenticateWithJSON
    def serve_reduced(self, id):
        """Return the reduced-size file data (i.e., resized image or ogg/mp3-
        converted wav) for the file in files/ with id=id or an error message if
        the file does not exist or the user is not authorized to access it.
        """
        return serveFile(id, True)


def serveFile(id, reduced=False):
    """Use FileApp to serve the content (binary data) of the file with id=id.  If
    reduced is True, then try to serve /files/reduced_files/<filename> where
    filename is file.lossyFilename.
    """
    file = Session.query(File).options(subqueryload(File.parentFile)).get(id)
    if getattr(file, 'parentFile', None):
        file = file.parentFile
    elif getattr(file, 'url', None):
        response.status_int = 400
        return json.dumps({'error': u'The content of file %s is stored elsewhere at %s' % (id, file.url)})
    if file:
        filesDir = config['app_conf']['permanent_store']
        if reduced:
            filename = getattr(file, 'lossyFilename', None)
            if not filename:
                response.status_int = 404
                return json.dumps({'error': u'There is no size-reduced copy of file %s' % id})
            filePath = os.path.join(filesDir, 'reduced_files', filename)
        else:
            filePath = os.path.join(filesDir, file.filename)
        unrestrictedUsers = h.getUnrestrictedUsers()
        if h.userIsAuthorizedToAccessModel(session['user'], file, unrestrictedUsers):
            return forward(FileApp(filePath))
        else:
            response.status_int = 403
            return json.dumps(h.unauthorizedMsg)
    else:
        response.status_int = 404
        return json.dumps({'error': 'There is no file with id %s' % id})

################################################################################
# File Create Functionality
################################################################################

def getUniqueFilePath(filePath):
    """This function ensures a unique file path (without race conditions) by
    attempting to create the file using os.open.  If the file exists, an OS
    error is raised (or if the file is too long, an IO error is raised), and
    a new file path/name is generated until a unique one is found.  Returns
    an ordered pair: (<file object>, <unique file path>).
    """
    filePathParts = os.path.splitext(filePath) # returns ('/path/file', '.ext')
    while 1:
        try:
            fileDescriptor = os.open(filePath, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            return os.fdopen(fileDescriptor, 'wb'), unicode(filePath)
        except (OSError, IOError):
            pass
        filePath = u'%s_%s%s' % (filePathParts[0][:230],
                    ''.join(sample(digits + letters, 8)), filePathParts[1])

def addStandardMetadata(file, data):
    """Add the metadata that all JSON-created file creation requests can add."""
    file.description = h.normalize(data['description'])
    file.utteranceType = data['utteranceType']
    file.dateElicited = data['dateElicited']
    if data['elicitor']:
        file.elicitor = data['elicitor']
    if data['speaker']:
        file.speaker = data['speaker']
    file.tags = [t for t in data['tags'] if t]
    file.forms = [f for f in data['forms'] if f]
    now = h.now()
    file.datetimeEntered = now
    file.datetimeModified = now
    file.enterer = session['user']
    return file

def restrictFileByForms(file):
    """Restrict the entire file if it is associated to restricted forms."""
    tags = [f.tags for f in file.forms]
    tags = [tag for tagList in tags for tag in tagList]
    restrictedTags = [tag for tag in tags if tag.name == u'restricted']
    if restrictedTags:
        restrictedTag = restrictedTags[0]
        if restrictedTag not in file.tags:
            file.tags.append(restrictedTag)
    return file

class InvalidFieldStorageObjectError(Exception):
    pass

def createBase64File(data):
    """Create and return an OLD file model generated from a data dict that
    contains a 'base64EncodedFile' key whose value should be a base64 encoded
    file.
    """
    data['MIMEtype'] = u''  # during validation, the schema will set a proper value based on the base64EncodedFile or filename attribute
    schema = FileCreateWithBase64EncodedFiledataSchema()
    state = h.State()
    state.full_dict = data
    state.user = session['user']
    data = schema.to_python(data, state)

    file = File()
    file.MIMEtype = data['MIMEtype']
    file.filename = h.normalize(data['filename'])

    file = addStandardMetadata(file, data)

    # Write the file to disk (making sure it's unique and thereby potentially)
    # modifying file.filename; and calculate file.size.
    fileData = data['base64EncodedFile']     # base64-decoded during validation
    filesPath = config['app_conf']['permanent_store']
    filePath = os.path.join(filesPath, file.filename)
    fileObject, filePath = getUniqueFilePath(filePath)
    file.filename = os.path.split(filePath)[-1]
    file.name = file.filename
    fileObject.write(fileData)
    fileObject.close()
    fileData = None
    file.size = os.path.getsize(filePath)

    file = restrictFileByForms(file)
    return file

def createExternallyHostedFile(data):
    """Create and return an OLD file model generated from a data dict that
    contains a 'url' key whose value should be a valid url where the file is
    served.  Optional attributes: name, password, MIMEtype.
    """
    data['password'] = data.get('password') or u''
    schema = FileExternallyHostedSchema()
    data = schema.to_python(data)
    file = File()

    # User-inputted string data
    file.name = h.normalize(data['name'])
    file.password = data['password']
    file.MIMEtype = data['MIMEtype']
    file.url = data['url']

    file = addStandardMetadata(file, data)
    file = restrictFileByForms(file)
    return file

def createSubintervalReferencingFile(data):
    """Create and return an OLD file model generated from a data dict that
    contains a 'parentFile' key whose value must be a foreign key id that
    references another file, which file must be an audio or video file.  The
    data dict should also contain a 'name' key whose value can be a name that is
    distinct from the filename value of the parent file (the child/referencing
    file has no value for filename.)  The referencing subinterval file must also
    contain float values for the 'start' and 'end' attributes which indicate the
    subinterval of the parent file that constitute the content of the
    referencing file.

    As with files created from base64-encoded file data (cf. createBase64File
    above), creation requests for referencing subinterval files may contain
    metadata such as a description, an utterance type, etc.

    Note that referencing files have no filename or size attributes.
    """
    data['name'] = data.get('name') or u''
    schema = FileSubintervalReferencingSchema()
    state = h.State()
    state.full_dict = data
    state.user = session['user']
    data = schema.to_python(data, state)

    file = File()

    # Data unique to referencing subinterval files
    file.parentFile = data['parentFile']
    file.name = h.normalize(data['name']) or file.parentFile.filename   # Name defaults to the parent file's filename if nothing provided by user
    file.start = data['start']
    file.end = data['end']
    file.MIMEtype = file.parentFile.MIMEtype

    file = addStandardMetadata(file, data)
    file = restrictFileByForms(file)

    return file

def createPlainFile():
    """Return an OLD file model generated from POST params (not JSON formatted).
    The usual file metadata can be submitted.  Unique to this method is the
    filedata key and the treatment of the filename value.
    
    1. 'filedata', a  cgi.FieldStorage object containing the file data.
    2. 'filename', a string (optional but encouraged, i.e., if not provided, the
       system will attempt to create one from the file path)

    Note that the schema expects not 'forms' and 'files' keys but 'forms-0',
    'forms-1', etc., as per the formencode.variabledecode.NestedVariables format.
    """

    values = dict(request.params)
    filedata = request.POST.get('filedata')
    if not hasattr(filedata, 'file'):
        raise InvalidFieldStorageObjectError
    if not values.get('filename'):
        values['filename'] = os.path.split(filedata.filename)[-1]
    values['filedataFirstKB'] = filedata.value[:1024]
    schema = FileCreateWithFiledataSchema()
    data = schema.to_python(values)

    file = File()
    file.filename = h.normalize(data['filename'])
    file.MIMEtype = data['MIMEtype']

    filesPath = config['app_conf']['permanent_store']
    filePath = os.path.join(filesPath, file.filename)
    fileObject, filePath = getUniqueFilePath(filePath)
    file.filename = os.path.split(filePath)[-1]
    file.name = file.filename
    shutil.copyfileobj(filedata.file, fileObject)
    filedata.file.close()
    fileObject.close()
    file.size = os.path.getsize(filePath)

    file = addStandardMetadata(file, data)

    return file

################################################################################
# File Update Functionality
################################################################################

def updateStandardMetadata(file, data, changed):

    changed = h.setAttr(file, 'description', h.normalize(data['description']), changed)
    changed = h.setAttr(file, 'utteranceType', h.normalize(data['utteranceType']), changed)
    changed = h.setAttr(file, 'dateElicited', data['dateElicited'], changed)
    changed = h.setAttr(file, 'elicitor', data['elicitor'], changed)
    changed = h.setAttr(file, 'speaker', data['speaker'], changed)

    # Many-to-Many Data: tags & forms
    # Update only if the user has made changes.
    formsToAdd = [f for f in data['forms'] if f]
    tagsToAdd = [t for t in data['tags'] if t]

    if set(formsToAdd) != set(file.forms):
        file.forms = formsToAdd
        changed = True

        # Cause the entire file to be tagged as restricted if any one of its
        # forms are so tagged.
        tags = [f.tags for f in file.forms]
        tags = [tag for tagList in tags for tag in tagList]
        restrictedTags = [tag for tag in tags if tag.name == u'restricted']
        if restrictedTags:
            restrictedTag = restrictedTags[0]
            if restrictedTag not in tagsToAdd:
                tagsToAdd.append(restrictedTag)

    if set(tagsToAdd) != set(file.tags):
        file.tags = tagsToAdd
        changed = True

    return file, changed

def updateFile(file):
    """Update the input File model object using the JSON object of the request
    body.  If changed is not set to true in the course of attribute setting,
    then False is returned and no update occurs.
    """
    changed = False
    schema = FileUpdateSchema()
    data = json.loads(unicode(request.body, request.charset))
    state = h.State()
    state.full_dict = data
    state.user = session['user']
    data = schema.to_python(data, state)
    file, changed = updateStandardMetadata(file, data, changed)
    if changed:
        file.datetimeModified = datetime.datetime.utcnow()
        return file
    return changed

def updateSubintervalReferencingFile(file):
    """Update the subinterval-referencing file model using the JSON object in
    the request body.  If changed is not set to true in the course of attribute
    setting, then False is returned and no update occurs.
    """
    changed = False
    schema = FileSubintervalReferencingSchema()
    data = json.loads(unicode(request.body, request.charset))
    data['name'] = data.get('name') or u''
    state = h.State()
    state.full_dict = data
    state.user = session['user']
    data = schema.to_python(data, state)

    # Data unique to referencing subinterval files
    changed = h.setAttr(file, 'parentFile', data['parentFile'], changed)
    changed = h.setAttr(file, 'name', (h.normalize(data['name']) or file.parentFile.filename), changed)
    changed = h.setAttr(file, 'start', data['start'], changed)
    changed = h.setAttr(file, 'end', data['end'], changed)

    file, changed = updateStandardMetadata(file, data, changed)

    if changed:
        file.datetimeModified = datetime.datetime.utcnow()
        return file
    return changed

def updateExternallyHostedFile(file):
    """Update the externally hosted file model using the JSON object in
    the request body.  If changed is not set to true in the course of attribute
    setting, then False is returned and no update occurs.
    """
    changed = False
    data = json.loads(unicode(request.body, request.charset))
    data['password'] = data.get('password') or u''
    data = FileExternallyHostedSchema().to_python(data)

    # Data unique to referencing subinterval files
    changed = h.setAttr(file, 'url', data['url'], changed)
    changed = h.setAttr(file, 'name', h.normalize(data['name']), changed)
    changed = h.setAttr(file, 'password', data['password'], changed)
    changed = h.setAttr(file, 'MIMEtype', data['MIMEtype'], changed)

    file, changed = updateStandardMetadata(file, data, changed)

    if changed:
        file.datetimeModified = datetime.datetime.utcnow()
        return file
    return changed


################################################################################
# Delete File Functionality
################################################################################

def deleteFile(file):
    """Delete the file object from the database and the file from the filesystem.
    If the file has a lossyFilename attribute, then files/reduced_files/<lossyFilename>
    is deleted from the filesystem also
    """
    if getattr(file, 'filename', None):
        filePath = os.path.join(config['app_conf']['permanent_store'], file.filename)
        os.remove(filePath)
    if getattr(file, 'lossyFilename', None):
        filePath = os.path.join(config['app_conf']['permanent_store'],
                                'reduced_files', file.lossyFilename)
        os.remove(filePath)
    Session.delete(file)
    Session.commit()


################################################################################
# New/Edit File Functionality
################################################################################

def getNewEditFileData(GET_params):
    """Return the data necessary to create a new OLD file or update an existing
    one.  The GET_params parameter is the request.GET dictionary-like object
    generated by Pylons.

    If no parameters are provided (i.e., GET_params is empty), then retrieve all
    data (i.e., tags, speakers, etc.) from the db and return it.

    If parameters are specified, then for each parameter whose value is a
    non-empty string (and is not a valid ISO 8601 datetime), retrieve and
    return the appropriate list of objects.

    If the value of a parameter is a valid ISO 8601 datetime string,
    retrieve and return the appropriate list of objects *only* if the
    datetime param does *not* match the most recent datetimeModified value
    of the relevant data store.  This makes sense because a non-match indicates
    that the requester has out-of-date data.
    """

    # Map param names to the OLD model objects from which they are derived.
    paramName2ModelName = {
        'tags': 'Tag',
        'speakers': 'Speaker',
        'users': 'User'
    }

    # map_ maps param names to functions that retrieve the appropriate data
    # from the db.
    map_ = {
        'tags': h.getMiniDictsGetter('Tag'),
        'speakers': h.getMiniDictsGetter('Speaker'),
        'users': h.getMiniDictsGetter('User')
    }

    # result is initialized as a dict with empty list values.
    result = dict([(key, []) for key in map_])
    result['utteranceTypes'] = h.utteranceTypes
    result['allowedFileTypes'] = h.allowedFileTypes

    # There are GET params, so we are selective in what we return.
    if GET_params:
        for key in map_:
            val = GET_params.get(key)
            # Proceed so long as val is not an empty string.
            if val:
                valAsDatetimeObj = h.datetimeString2datetime(val)
                if valAsDatetimeObj:
                    # Value of param is an ISO 8601 datetime string that
                    # does not match the most recent datetimeModified of the
                    # relevant model in the db: therefore we return a list
                    # of objects/dicts.  If the datetimes do match, this
                    # indicates that the requester's own stores are
                    # up-to-date so we return nothing.
                    if valAsDatetimeObj != h.getMostRecentModificationDatetime(
                    paramName2ModelName[key]):
                        result[key] = map_[key]()
                else:
                    result[key] = map_[key]()

    # There are no GET params, so we get everything from the db and return it.
    else:
        for key in map_:
            result[key] = map_[key]()

    return result
