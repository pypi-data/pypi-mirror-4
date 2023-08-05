import unittest
from plone.app.testing import login, setRoles, TEST_USER_NAME, TEST_USER_ID
from Products.ContentTypeValidator.validator import ContentTypeValidator
from Products.ContentTypeValidator.tests.base import CONTENTTYPEVALIDATOR_FUNCTIONAL


class TestContentTypeValidator(unittest.TestCase):

    layer = CONTENTTYPEVALIDATOR_FUNCTIONAL

    def setUp(self):
        testfiles_path = '../omelette/Products/ContentTypeValidator/tests/test_files/'
        self.portal = self.layer['portal']
        site = self.portal
        login(site, TEST_USER_NAME)
        setRoles(site, TEST_USER_ID, ('Manager',))
        types = {'txt': 'text/plain', 'gif': 'image/gif', 'odt': 'application/vnd.oasis.opendocument.text'}
        #create 3 ATFile of different formats (gif, odt, text) on the site, they will be used as the new field content
        #to be validated.
        for type, mimetype in types.iteritems():
            setattr(self, '%s_MIMETYPE' % type.upper(), mimetype)
            site.invokeFactory('File', id='%s_file' % type, file=file('%s%s_file.%s' % (testfiles_path, type, type)))
            setattr(self, '%s_file' % type, getattr(site, '%s_file' % type).getFile())
        self.schema_field = site.txt_file.getField('file')
        self.REQUEST = site.REQUEST

    def tearDown(self):
        #after each test remove all the validators but the default one, else they stack up
        while len(self.schema_field.validators) > 2:
            self.schema_field.validators._chain = self.schema_field.validators._chain[:-1]
            self.schema_field.validators._v_mode = self.schema_field.validators._v_mode[:-1]

    def test_ValidateFileWithoutContentTypeValidator(self):
        # no content type validator defined on the field, the validation should be ok for any (non-empty) file.
        site = self.portal
        self.assertEquals(self.schema_field.validate(self.txt_file, site.txt_file, REQUEST=self.REQUEST), None)
        self.assertEquals(self.schema_field.validate(self.gif_file, site.txt_file, REQUEST=self.REQUEST), None)
        self.assertEquals(self.schema_field.validate(self.odt_file, site.txt_file, REQUEST=self.REQUEST), None)

    def test_ValidateCorrectFileWithASingleValuedContentTypeValidator(self):
        site = self.portal
        #add the content type validator with a single value (gif mimetype) on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.GIF_MIMETYPE,)))
        self.assertEquals(self.schema_field.validate(self.gif_file, site.txt_file, REQUEST=self.REQUEST), None)

    def test_ValidateWrongFileWithASingleValuedContentTypeValidator(self):
        site = self.portal
        #add the content type validator with a single value (gif mimetype) on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.GIF_MIMETYPE,)))
        self.assertEquals(self.schema_field.validate(self.txt_file, site.txt_file, REQUEST=self.REQUEST),
                          "File has to be of one of the following content-types 'image/gif'")
        self.assertEquals(self.schema_field.validate(self.odt_file, site.txt_file, REQUEST=self.REQUEST),
                          "File has to be of one of the following content-types 'image/gif'")

    def test_ValidateCorrectFileWithAMultipleValuedContentTypeValidator(self):
        site = self.portal
        #add the content type validator with multiple values (gif, text and odt mimetypes) on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.GIF_MIMETYPE, self.ODT_MIMETYPE, self.TXT_MIMETYPE,)))
        #they should all pass as each of their mimetype is in the validator
        self.assertEquals(self.schema_field.validate(self.txt_file, site.txt_file, REQUEST=self.REQUEST), None)
        self.assertEquals(self.schema_field.validate(self.gif_file, site.txt_file, REQUEST=self.REQUEST), None)
        self.assertEquals(self.schema_field.validate(self.odt_file, site.txt_file, REQUEST=self.REQUEST), None)

    def test_ValidateWrongFileWithAMultipleValuedContentTypeValidator(self):
        site = self.portal
        #add the content type validator with multiple values (gif and odt mimetypes) on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.GIF_MIMETYPE, self.ODT_MIMETYPE,)))
        self.assertEquals(self.schema_field.validate(self.txt_file, site.txt_file, REQUEST=self.REQUEST),
                          "File has to be of one of the following content-types 'image/gif, application/vnd.oasis.opendocument.text'")

    def test_ValidateWhenDeleteFieldContent(self):
        site = self.portal
        #add the content type validator on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.GIF_MIMETYPE,)))
        #simulate a deletion of the field content
        self.REQUEST.form.update({'file_delete': 'delete'})
        #the validation should not do check anything since the field will be emptied
        self.assertEquals(self.schema_field.validate(self.odt_file, site.txt_file, REQUEST=self.REQUEST), None)

    def test_ValidateNoChangeInFieldContentWithCorrectType(self):
        site = self.portal
        #add the content type validator with text mimetype on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.TXT_MIMETYPE,)))
        #simulate no changes in the field content
        self.REQUEST.form.update({'file_delete': 'nochange'})
        self.assertEquals(self.schema_field.validate(self.txt_file, site.txt_file, REQUEST=self.REQUEST), None)

    def test_ValidateNoChangeInFieldContentWithWrongType(self):
        site = self.portal
        #add the content type validator with GIF mimetype on the AT field
        self.schema_field.validators.append(ContentTypeValidator((self.GIF_MIMETYPE,)))
        #simulate no changes in the field content
        self.REQUEST.form.update({'file_delete': 'nochange'})
        #the validation should fail as the original content is a txt file and the mymetype checked is now gif
        self.assertEquals(self.schema_field.validate(self.txt_file, site.txt_file, REQUEST=self.REQUEST),
                          "File has to be of one of the following content-types 'image/gif'")
