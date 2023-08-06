from dm.dom.stateful import *
import dm.dom.person
import kforge.regexps
from dm.dom.meta import AttributeValidator
from kforge.exceptions import ValidationError

class Person(dm.dom.person.Person):
    "Registered person."

    memberships = AggregatesMany('Member', key='project', isEditable=False)
    sshKeys = AggregatesMany('SshKey', key='id', isHidden=True)


class ValidateSshKey(AttributeValidator):

    def validate(self):
        # Check key string is available.
        attrName = self.metaAttr.name
        if attrName in self.objectData:
            attrValue = self.objectData[attrName]
            attrValue = attrValue.strip()
            publicKey = attrValue.split(' ')[1]
            if self.domainObject and (getattr(self.domainObject, attrName) == attrValue):
                pass
            elif self.objectRegister.registry.sshKeys.search(publicKey):
                msg = "Key has already been registered on this site."
                raise ValidationError(msg)
            # Check key decodes from base64.
            try:
                publicKey.decode('base64')
            except:
                msg = "Key does not appear to be encoded with base64."
                raise ValidationError(msg)


class SshKey(DatedStatefulObject):

    searchAttributeNames = ['keyString']

    keyString = Text(regex=kforge.regexps.sshKeyString, validators=[ValidateSshKey])
    person = HasA('Person')
    isConsummated = Boolean(isHidden=True)


