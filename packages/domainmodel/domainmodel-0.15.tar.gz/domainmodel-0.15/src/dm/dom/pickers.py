class ModelPicker(object):

    def __init__(self, domainClassMeta, ignore=[]):
        self.domainClassMeta = domainClassMeta
        self.ignore = ignore

    def pick(self):
        attributes = []
        if not hasattr(self.domainClassMeta, 'attributes'):
            help(self.domainClassMeta)
        for attribute in self.domainClassMeta.attributes:
            if attribute.name in self.ignore:
                continue
            if self.isAttributeIncluded(attribute):
                attributes.append(attribute)
        return attributes

    def isAttributeIncluded(self, attribute):
        return False


class GetInitableAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        # Only the editable attributes, and implicit associate lists.
        return attribute.isEditable and not (attribute.isAssociateList and not attribute.getDomainClass().isImplicitAssociation)


class GetReadableAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        return not attribute.isHidden and not (attribute.isAssociateList and attribute.isPagedList)


class GetEditableAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        # Only the editable attributes that are not immutable, and implicit associate lists.
        return attribute.isEditable and not attribute.isImmutable and not (attribute.isAssociateList and not attribute.getDomainClass().isImplicitAssociation)

   
class GetAdminInitableAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        # Only non-system attributes, and implicit associate lists.
        return not attribute.isSystem and not (attribute.isAssociateList and not attribute.getDomainClass().isImplicitAssociation)

   
class GetAdminReadableAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        return not (attribute.isAssociateList and attribute.isPagedList)


class GetAdminEditableAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        return not attribute.isSystem and not attribute.isImmutable and not (attribute.isAssociateList and not attribute.getDomainClass().isImplicitAssociation)

   
class GetMigrationAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        # Exclude all associate lists.
        return not attribute.isAssociateList


class GetAllAttributes(ModelPicker):

    def isAttributeIncluded(self, attribute):
        return True

