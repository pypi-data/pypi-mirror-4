from dm.ioc import *
import dm.webkit
from dm.webkit import Manipulator
from dm.webkit import htmlescape
from dm.webkit import SortedDict, MultipleChoiceField
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
from dm.exceptions import *
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from dm.dom.meta import Text
import traceback
import re
import weakref
moddebug = False

class BaseManipulator(Manipulator):
    "Supertype for presentation forms."

    registry   = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    commands   = RequiredFeature('CommandSet')
    logger     = RequiredFeature('Logger')
    webkit     = dm.webkit

    sizeSelectMultiple = 4

    base_fields = []  # Django 1.0.

    def __init__(self, *args, **kwds):
        super(BaseManipulator, self).__init__(*args, **kwds)
        self.manipulationErrors = {}
        self.validationErrors = {}
        self.extnManipulator = None

    def wrap(self):
        if hasattr(self, 'cleaned_data'):
            data = self.cleaned_data
        elif hasattr(self, 'data'):
            data = self.data
        else:
            raise Exception, "There is no form data to wrap."
        return FormWrapper(self, data, self.getErrors())

    def validate(self, data):
        """Validates given data against form fields."""
        self._validate(data)
        if self.extnManipulator:
            self.extnManipulator.validate(data)

    def _validate(self, data):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            self.cleaned_data = data
        else:
            self.validationErrors = {}
            self.data = data
            self.is_bound = True
            self.full_clean()
            # Property self.errors => BaseForm._get_errors() => ErrorDict.
            for (attrName, error) in self.errors.items():
                self.validationErrors[attrName] = error.as_text().strip('* ')
            if self.validationErrors:
                raise FormError(self.validationErrors.copy())

    def getErrors(self):
        errors = {}
        errors.update(self.validationErrors)
        errors.update(self.manipulationErrors)
        return errors

    def isTwoCharsMin(self, field_data, all_data):
        self.isTooShort(field_data, 2)

    def isThreeCharsMin(self, field_data, all_data):
        self.isTooShort(field_data, 3)

    def isFourCharsMin(self, field_data, all_data):
        self.isTooShort(field_data, 4)

    def isFifteenCharsMax(self, field_data, all_data):
        self.isTooLong(field_data, 15)

    def isTwentyCharsMax(self, field_data, all_data):
        self.isTooLong(field_data, 20)

    def is255CharsMax(self, field_data, all_data):
        self.isTooLong(field_data, 255)
  
    def isTooLong(self, field_data, limit):
        if (len(field_data.strip()) > limit):
            raise dm.webkit.ValidationError("This field is too long.")
  
    def isTooShort(self, field_data, limit):
        if (len(field_data.strip()) < limit):
            raise dm.webkit.ValidationError("This field is too short.")


class DomainObjectManipulator(BaseManipulator):
    "Supertype for domain object forms."

    def __init__(self, objectRegister,
            domainObject=None, fieldNames=[], client=None, pickerClass=None):
        super(DomainObjectManipulator, self).__init__()
        self.client = client
        self.pickerClass = pickerClass
        self.objectRegister = objectRegister
        self.metaObject = self.objectRegister.getDomainClassMeta()
        self.domainObject = domainObject
        msg = "Building %s for %s." % (
            self.__class__.__name__, self.metaObject.name
        )
        self.logger.debug(msg)
        self.fieldNames = fieldNames
        # Pick fields.
        self.pickFields()
        msg = "Built %s form with fields: %s" % (
            self.__class__.__name__, ", ".join(self.fieldNames)
        )
        self.logger.debug(msg)
        # Setup extention.
        domainClass = self.objectRegister.getDomainClass()
        if domainClass.hasModelExtn and domainObject:
            # The class uses plugins which may extend the model.
            extnRegister = domainObject.getExtnRegister()
            if extnRegister:
                extnObject = domainObject.getExtnObject()
                self.extnManipulator = DomainObjectManipulator(
                    objectRegister=extnRegister,
                    domainObject=extnObject,
                    pickerClass=self.pickerClass,
                )

    def getClient(self):
        if self._client:
            return self._client()
        else:
            return self._client
    def setClient(self, client):
        if client:
            client = weakref.ref(client)
        self._client = client
    client = property(getClient, setClient)

    def pickFields(self):
        self.fieldedMetaAttrs = []
        if self.fieldNames:
            msg = "Building fields from fieldNames..."
            msg += "%s." % ", ".join(self.fieldNames)
            self.logger.debug(msg)
            for fieldName in self.fieldNames:
                if fieldName in self.metaObject.attributeNames:
                    metaAttr = self.metaObject.attributeNames[fieldName]
                else:
                    raise Exception, "Field name '%s' not defined in meta for domain class '%s' (but %s are)." % (fieldName, self.metaObject.name, self.metaObject.attributeNames.keys())
                self.fieldedMetaAttrs.append(metaAttr)
        else:
            self.fieldNames = []
            if self.pickerClass:
                msg = "Building fields from meta object using picker class '%s'." % self.pickerClass
                self.logger.debug(msg)
                for metaAttr in self.pickAttributes():
                    self.fieldedMetaAttrs.append(metaAttr)
            else:
                msg = "Building fields from meta object using isAttrExcluded() method."
                self.logger.debug(msg)
                for metaAttr in self.metaObject.attributes:
                    if self.isAttrExcluded(metaAttr):
                        msg = "Excluded '%s' attribute." % metaAttr.name
                        self.logger.debug(msg)
                    else:
                        self.fieldedMetaAttrs.append(metaAttr)
            self.fieldNames = [i.name for i in self.fieldedMetaAttrs]

    def isAttrExcluded(self, metaAttr):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return False
        if self.isAttrNameExcluded(metaAttr.name):
            return True
        if not metaAttr.isEditable:
            return True
        return False

    def isAttrNameExcluded(self, attrName):
        if self.fieldNames and not attrName in self.fieldNames:
            return True
        return False
    
    def setFields(self, fields):
        pass # Accept setting of deep copy of base_fields in parent.
    
    def getFields(self):
        if not hasattr(self, '_fields'):
            self._fields = SortedDict()
            self.buildFields()
        return self._fields

    def buildFields(self):
        for metaAttr in self.fieldedMetaAttrs:
            self.setField(metaAttr.name, self.createField(metaAttr))

    def setField(self, name, field):
        self._fields[name] = field

    fields = property(getFields, setFields)

    def createField(self, metaAttr):
        field = None
        isFieldRequired = metaAttr.isRequired
        self.logger.debug("Building form field: %s" % metaAttr.name)
        if metaAttr.isAssociateList:
            choices = metaAttr.getAllChoices(objectRegister=self.objectRegister, domainObject=self.domainObject)
            if moddebug:
                msg = "Choices for '%s': %s" % (metaAttr.name, choices)
                self.logger.debug(msg)
            # Todo: Write test to check for this (was: ChoiceField).
            field = self.webkit.MultipleChoiceField(
                required=isFieldRequired,
                choices=choices,
            )
        elif metaAttr.isDomainObjectRef:
            choices = metaAttr.getAllChoices(objectRegister=self.objectRegister, domainObject=self.domainObject)
            if moddebug:
                msg = "Choices for '%s': %s" % (metaAttr.name, choices)
                self.logger.debug(msg)
            # Todo: Revert this 'True', and introduce Ajax auto-completion
            # instead of drop-down when more than count limit.
            if True:  # len(choices) <= 50:
                choices = [(u'', u'-- select option --')] + choices
                field = self.webkit.ChoiceField(
                    required=isFieldRequired,
                    choices=choices,
                )
            else:  # need to find a way to only do this for string keys
                field = self.webkit.CharField(
                    required=isFieldRequired,
                    choices=choices,
                )
        elif metaAttr.isValueObject():
            if metaAttr.typeName == 'String':
                if metaAttr.name[0:5] == 'email':
                    field = self.webkit.EmailField(
                        required=isFieldRequired,
                        min_length=metaAttr.minLength,
                        max_length=metaAttr.maxLength,
                    )
                else:
                    if metaAttr.getChoices:
                        choices = metaAttr.getChoices()
                        field = self.webkit.ChoiceField(
                            choices=[(u'', u'-- select option --')] + choices,
                            required=isFieldRequired,
                        )
                    elif metaAttr.regex:
                        field = self.webkit.RegexField(
                            required=isFieldRequired,
                            regex=metaAttr.regex,
                            min_length=metaAttr.minLength,
                            max_length=metaAttr.maxLength,
                        )
                    else:
                        field = self.webkit.CharField(
                            required=isFieldRequired,
                            min_length=metaAttr.minLength,
                            max_length=metaAttr.maxLength,
                        )
            elif metaAttr.typeName == 'MarkdownText':
                field = self.webkit.CharField(
                    required=isFieldRequired,
                    widget=self.webkit.widgets.Textarea(),
                    min_length=metaAttr.minLength,
                    max_length=metaAttr.maxLength,
                )
            elif isinstance(metaAttr, Text):
                if metaAttr.regex:
                    field = self.webkit.RegexField(
                        required=isFieldRequired,
                        widget=self.webkit.widgets.Textarea(),
                        regex=metaAttr.regex,
                        min_length=metaAttr.minLength,
                        max_length=metaAttr.maxLength,
                    )
                else:
                    field = self.webkit.CharField(
                        required=isFieldRequired,
                        widget=self.webkit.widgets.Textarea(),
                        min_length=metaAttr.minLength,
                        max_length=metaAttr.maxLength,
                    )
            elif metaAttr.typeName == 'Password':
                isFieldRequired = self.domainObject == None
                field = self.webkit.CharField(
                    required=isFieldRequired,
                    widget=dm.webkit.widgets.PasswordInput,
                    min_length=metaAttr.minLength,
                    max_length=metaAttr.maxLength,
                )
            elif metaAttr.typeName == 'Url':
                field = self.webkit.URLField(
                    required=isFieldRequired,
                    min_length=metaAttr.minLength,
                    max_length=metaAttr.maxLength,
                )
            elif metaAttr.typeName == 'Integer':
                field = self.webkit.IntegerField(
                    required=isFieldRequired,
                    min_value=metaAttr.minValue,
                    max_value=metaAttr.maxValue,
                )
            elif metaAttr.typeName == 'Boolean':
                field = self.webkit.BooleanField(required=isFieldRequired)
            elif metaAttr.typeName == 'DateTime':
                field = self.webkit.DateTimeField(required=isFieldRequired)
            elif metaAttr.typeName == 'Date':
                field = self.webkit.DateField(required=isFieldRequired)
            elif metaAttr.typeName == 'RDate': # Todo: Remove this type.
                field = self.webkit.DateField(required=isFieldRequired)
            else:
                field = self.webkit.CharField(required=isFieldRequired)
        elif metaAttr.typeName == 'ImageFile':
            field = self.webkit.ImageField(
                required=isFieldRequired,
            )
        if field:
            field.metaAttr = metaAttr
            field.field_comment = metaAttr.comment
            field.field_title = metaAttr.calcTitle()
            field.field_name = metaAttr.name
            self.fields[metaAttr.name] = field
        else:
            message = "Can't build form field for meta attribute: %s" % metaAttr
            self.logger.critical(message)
            raise Exception, message
        return field

    def clean(self):
        "Validate data."
        # This hook method is called from BaseForm.full_clean().
        # Validate attribute values against attribute model.
        for metaAttr in self.pickAttributes():
            try:
                metaAttr.validateValue(
                    self.cleaned_data,
                    self.domainObject, 
                    self.objectRegister
                )
            except ValidationError, inst:
                self.appendFieldError(metaAttr.name, inst.args[0])

        # The BaseForm.full_clean() method expects cleaned_data to be returned.
        return self.cleaned_data

    def setCleanedData(self, data):
        self.cleaned_data = data
        if self.extnManipulator:
            self.extnManipulator.setCleanedData(data)

    def appendFieldError(self, attrName, errorMsg):
        if attrName not in self._errors:
            self._errors[attrName] = dm.webkit.fields.ErrorList([errorMsg])
        else:
            self._errors[attrName].append(errorMsg)

    def create(self, data):
        """Create a new domain object from given data."""
        self._validate(data)
        self.manipulationErrors = {}
        self.isSystemError = False
        try:
            self.createObjectKwds()
            self.createDomainObject()
            try:
                self.setAssociateListAttributes()
            except:
                self.logger.error("Model: Caught exception raised whilst setting associate list attributes on new domain object. Attempting to uncreate new domain object...")
                try:
                    self.domainObject.uncreate()
                except Exception, inst:
                    trace = traceback.format_exc()
                    self.logger.error("Model: Failed to uncreate new domain object: %s" % trace)
                else:
                    self.logger.error("Model: Uncreated new domain object OK. ")
                self.logger.error("Model: Reraising exception raised whilst setting assocate list attributes on new domain object... ")
                raise
        except:
            msg = self.formatSystemError(data, 'creating')
            self.logger.error(msg)
            self.manipulationErrors = {'': "System error has been logged."}
            self.isSystemError = True
        if self.manipulationErrors:
            raise FormError(self.manipulationErrors.copy(), isSystemError=self.isSystemError)
        if self.extnManipulator:
            self.extnManipulator.create(data)
        
    def createObjectKwds(self):
        self.objectKwds = {}
        fieldedAttrs = self.getFieldedNonAssociateListMetaAttrs()
        data = self.cleaned_data
        domValues = self.presentationToDomainValues(data, fieldedAttrs)
        for (attrName, domValue) in domValues.items():
            if not domValue == None:
                self.objectKwds[attrName] = domValue

    def createDomainObject(self):
        commandClass = self.getCreateCommandClass()
        if commandClass:
            objectKwds = self.objectKwds
            command = commandClass(**objectKwds)
        else:
            commandClass = self.getCommandClass('DomainObjectCreate')
            commandKwds = {}
            commandKwds['typeName'] = self.metaObject.name
            commandKwds['objectKwds'] = self.objectKwds
            command = commandClass(**commandKwds)
        command.execute()
        if not command.object:
            raise Exception, "Create command did not produce an object."
        self.domainObject = command.object

    def getCreateCommandClass(self):
        return self.getDomainObjectCommandClass('Create')
        
    def getDomainObjectCommandClass(self, actionName):
        domainClassName = self.metaObject.name
        commandClassName = domainClassName + actionName
        return self.getCommandClass(commandClassName)
        
    def getCommandClass(self, className):
        if className in self.commands:
            return self.commands[className]
        return None

    # Todo: Make explicit what happens when field has no value in cleaned_data. Issues: form submissions don't
    # include values that aren't set such as checkboxes. But we don't want to unset items that e.g. aren't included in API submissions.
    def getFieldedNonAssociateListMetaAttrs(self):
        metaAttrs = {}
        for metaAttr in self.metaObject.attributes:
            if metaAttr.name in self.fieldNames:
                if not metaAttr.isAssociateList:
                    # Must include Boolean attributes, need to find out what depends on excluding unsubmitted values.
                    # Todo: Test we can set Boolean attributes to false values through the registry views.
                    metaAttrs[metaAttr.name] = metaAttr
            elif metaAttr.isValueRef and metaAttr.isBoolean:
                metaAttrs[metaAttr.name] = metaAttr
        return metaAttrs

    def getFieldedAssociateListMetaAttrs(self):
        metaAttrs = {}
        for metaAttr in self.metaObject.attributes:
            if metaAttr.name in self.fieldNames:
                if metaAttr.isAssociateList:
                    metaAttrs[metaAttr.name] = metaAttr
        return metaAttrs

    # Todo: Rename MultiValueDict as PresentationObject.
    def presentationToDomainValues(self, multiValueDict, fieldedAttrs):
        domValues = {}
        for (attrName, metaAttr) in fieldedAttrs.items():
            if attrName in multiValueDict:
                try:
                    domValue = metaAttr.makeValueFromMultiValueDict(multiValueDict)
                    domValues[attrName] = domValue
                except Exception, inst:
                    trace = traceback.format_exc()
                    msg = "Can't get '%s' from presented value." % attrName
                    self.logger.error(msg + "\n" + trace)
                    raise Exception, msg
        return domValues

    def update(self, data):
        """Update an existing domain object from given data."""
        self._validate(data)
        self.manipulationErrors = {}
        self.isSystemError = False
        try:
            self.setNonAssociateListAttributes()
            self.setAssociateListAttributes()
        except:
            msg = self.formatSystemError(data, 'updating')
            self.logger.error(msg)
            self.manipulationErrors = {'': "System error has been logged."}
            self.isSystemError = True
        if self.manipulationErrors:
            raise FormError(self.manipulationErrors.copy(), isSystemError=self.isSystemError)
        if self.extnManipulator:
            self.extnManipulator.update(data)

    def formatSystemError(self, data, activity):
        callstack = "".join(traceback.format_stack()[:-2])
        trace = traceback.format_exc()
        msg = """System error %s object. See below for details.\n\n\
Submitted data: %s\n\n\
Callstack (see below for traceback):\n\
%s\n%s\n""" % (activity, data, callstack, trace)
        return msg

    def setNonAssociateListAttributes(self):
        if self.getFieldedNonAssociateListMetaAttrs():
            self.setAttributesFromMultiValueDict(self.domainObject, self.cleaned_data)
            self.domainObject.save()
       
    def setAttributesFromMultiValueDict(self, domainObject, multiValueDict):
        fieldedAttrs = self.getFieldedNonAssociateListMetaAttrs()
        attrValues = self.presentationToDomainValues(multiValueDict, fieldedAttrs)
        msg = "Updating fielded attributes '%s' with domain values '%s' derived from presentation values '%s'." % (
            str(fieldedAttrs.keys()), str(attrValues), str(multiValueDict)
        )
        self.logger.debug(msg)
        for attrName in fieldedAttrs:
            if attrName in attrValues:
                metaAttr = fieldedAttrs[attrName]
                attrValue = attrValues[attrName]
                # Check value is unchanged.
                if attrValue != metaAttr.getAttributeValue(domainObject):
                    msg = "Setting '%s' attribute to '%s'." % (attrName, attrValue)
                    self.logger.debug(msg)
                    metaAttr.setAttributeValue(domainObject, attrValue)

    def setAssociateListAttributes(self):
        for metaAttr in self.getFieldedAssociateListMetaAttrs().values():
            self.setAssociateListAttribute(metaAttr)
           
    def setAssociateListAttribute(self, metaAttr):
        # Todo: Test for setting (and clearing!) lists of associates.
        if metaAttr.name not in self.cleaned_data:
            #raise Exception, self.cleaned_data
            if hasattr(self.cleaned_data, 'setlist'):
                # MultiValuDict (Django 0.96, and tests?)
                # And also when unsetting licenses in KForge, there's a QueryDict.
                self.cleaned_data.setlist(metaAttr.name, [])
            else:
                # Normal Python dict.
                self.cleaned_data[metaAttr.name] = []
        metaAttr.setAttributeFromMultiValueDict(self.domainObject, self.cleaned_data)

    # Todo: Check if this method is still used anywhere.
    def getAttributeField(self, attrName):
        for field in self.fields:
            if attrName == field.field_name:
                return field
        return None

    def getUpdateParams(self):
        # Form fields are initialized with these data. 
        self.initial = self.domainObjectAsDictValues()
        if self.extnManipulator:
            self.initial.update(self.extnManipulator.getUpdateParams())
        return self.initial

    def domainObjectAsDictValues(self, absoluteUriPrefix=None):
        # Present object data for reading (include owner so backlinks are created in API).
        names = [a.name for a in self.pickAttributes(isOwnerIncluded=True)]
        return self.domainObject.asDictValues(names, absoluteUriPrefix=absoluteUriPrefix)

    def domainObjectAsNamedValues(self):
        # Present object data for reading (don't include owner because links are already in page).
        names = [a.name for a in self.pickAttributes(isOwnerIncluded=False)]
        return self.domainObject.asNamedValues(names)

    def pickAttributes(self, isOwnerIncluded=False):
        r = self.objectRegister
        ignore = []
        if not isOwnerIncluded:
            ignore += [r.ownerName, r.ownerName2]
        picker = self.pickerClass(self.metaObject, ignore=ignore)
        return picker.pick()


class HasManyManipulator(DomainObjectManipulator):
    "Domain object 'HasMany' attribute form."

    def isAttrExcluded(self, metaAttr):
        if DomainObjectManipulator.isAttrExcluded(self, metaAttr):
            return True 
        if metaAttr.isAssociateList:
            return True
        return False

    def isAttrNameExcluded(self, attrName):
        if attrName == self.objectRegister.ownerName:
            return True
        if attrName == self.objectRegister.ownerName2:
            return True
        if attrName == 'state':
            return True
        return False
    
    def createDomainObject(self):
        objectKwds = self.objectKwds
        self.domainObject = self.objectRegister.create(**objectKwds)


class FormWrapper(object):
    """
    A wrapper linking a form to the HTML template system.
    This allows dictionary-style lookups of formfields. It also handles feeding
    prepopulated data and validation error messages to the formfield objects.
    """
    
    def __init__(self, manipulator, data, error_dict): 
        self.manipulator = manipulator
        self.data = data
        self.error_dict = error_dict
        self.fields = self.wrapManipulatorFields()
#        self.plugin_fields = self.wrapPluginFields()
        if manipulator.extnManipulator:
            self.extnForm = manipulator.extnManipulator.wrap()

    def __repr__(self):
        return repr(self.data)

#    def getErrorMessages(self):
#        errorMessages = []
#        for field in self.fields:
#            if field.error:
#                errorMessages.append(mark_safe(field.error))
#        for error in self.error_dict.get('', []):
#            if error:
#                errorMessages.append(mark_safe(error))
#        return errorMessages

    def wrapManipulatorFields(self):
        wrappedFields = []
        for fieldName in self.manipulator.fieldNames:
            boundField = self.manipulator.__getitem__(fieldName)
            wrappedField = self.wrapBoundField(fieldName, boundField)
            wrappedFields.append(wrappedField)
        return wrappedFields

    def wrapPluginFields(self):
        wrappedFields = []
        if not hasattr(self.manipulator, 'pluginFields'):
            return wrappedFields
        for pluginField in self.manipulator.pluginFields:
            indication = ""
            if pluginField.is_required:
                indication = "<strong>*</strong>"
            wrappedField = "<label for=\"id_%s\">%s %s</label><br />" % (
                pluginField.field_name,
                pluginField.field_title,
                indication
            )
            wrappedField += "%s <br />" % self[pluginField.field_name]
            wrappedField += "<p class=\"desc\">%s</p>" % pluginField.field_comment
            wrappedFields.append(wrappedField)

        return wrappedFields

    def wrapBoundField(self, fieldName, field): 
        field.field_name = fieldName
        data = self.data.get(fieldName, None)
        if data is None:
            data = ''
        fieldError = self.error_dict.get(fieldName)
        return FormFieldWrapper(field, data, fieldError)

    def __getitem__(self, key):
        fieldName = key
        boundField = self.manipulator.__getitem__(fieldName)
        return self.wrapBoundField(fieldName, boundField)

    def has_errors(self):
        return self.hasErrors()

    def hasErrors(self):
        #return self.error_dict != {}
        return bool(self.error_dict)
        
# Todo: Test for incorrect setting of multiplechoicefield data (only one value was being selected).
class FormFieldWrapper(object):
    "A bridge between the template system and an individual form field. Used by FormWrapper."
    
    def __init__(self, formfield, data, field_error):
        self.formfield = formfield
        self.data = data
        self.field_error = field_error
        self.field_name = self.formfield.field_name
        field = self.formfield.field
        if hasattr(field, 'required'):
            self.field_required = field.required
        if hasattr(field, 'field_title'):
            self.field_title = field.field_title
        if hasattr(field, 'field_comment'):
            self.field_comment = field.field_comment
        elif hasattr(field, 'help_text'):
            self.field_comment = field.help_text
    #    self.error = self.makeErrorMessage()

    #def makeErrorMessage(self):
    #    message = ''
    #    if self.field_error:
    #        message = mark_safe(conditional_escape(force_unicode(self.field_error)))
    #    thisFieldPattern = re.compile('This field')
    #    thisValuePattern = re.compile('this value')
    #    validValuePattern = re.compile('valid value')
    #    confirmationPattern = re.compile('confirmation')
    #    underscorePattern = re.compile('_')
    #    fieldName = self.field_name
    #    message = thisFieldPattern.sub(fieldName.capitalize(), message)
    #    message = thisValuePattern.sub(fieldName, message)
    #    message = validValuePattern.sub('valid '+fieldName, message)
    #    message = confirmationPattern.sub(' confirmation', message)
    #    message = underscorePattern.sub(' ', message)
    #    return message

    def __unicode__(self):
        html = (force_unicode(self.formfield))
        if self.field_error:
            html = u'<div class="field-with-error">' + html + u'</div>'
        return mark_safe(html)

    def __str__(self):
        "Renders the field"
        return self.__unicode__()

    def __repr__(self):
        return '<FormFieldWrapper for "%s">' % self.formfield.field_name
    
    def field_list(self):
        """
        Like __str__(), but returns a list. Use this when the field's render()
        method returns a list.
        """
        return self.formfield.render(self.data)


