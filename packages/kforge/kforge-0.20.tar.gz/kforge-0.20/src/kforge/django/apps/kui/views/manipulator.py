from dm.view.manipulator import BaseManipulator
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.webkit import webkitName, webkitVersion
import dm.webkit as webkit
from kforge.ioc import *
from kforge.exceptions import KforgeCommandError
import re
import kforge.regexps
import kforge.command

class PasswordField(webkit.fields.RegexField):

    widget = webkit.fields.PasswordInput

    def __init__(self, *args, **kwargs):
        kwargs['regex'] = '^\S{4,}$' 
        kwargs['min_length'] = 4 
        super(PasswordField, self).__init__(*args, **kwargs)


class PasswordConfirmationField(webkit.fields.Field):

    widget = webkit.fields.PasswordInput

    def __init__(self, *args, **kwargs):
        super(PasswordConfirmationField, self).__init__(*args, **kwargs)


class PersonNameField(webkit.fields.RegexField):

    def __init__(self, *args, **kwargs):
        regex = '^(?!%s)%s$' % (kforge.regexps.reservedPersonName, kforge.regexps.personName)
        kwargs['required'] = True
        kwargs['regex'] = regex 
        kwargs['min_length'] = 2
        kwargs['max_length'] = 20
        super(PersonNameField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(PersonNameField, self).clean(value)
        # Check name is available.
        command = kforge.command.AllPersonRead(value)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Login name is already being used by another person."
            raise webkit.ValidationError(message)
        return value


class PersonManipulator(DomainObjectManipulator):

    #def isCaptchaCorrect(self, field_data, all_data):
    #    if self.dictionary['captcha.enable']:
    #        word = all_data['captcha']
    #        hash = all_data['captchahash']
    #        if not word and not hash:
    #            raise webkit.ValidationError("Captcha failure.")
    #        read = kforge.command.CaptchaRead(hash)
    #        try:
    #            read.execute()
    #        except KforgeCommandError, inst: 
    #            raise webkit.ValidationError("Captcha failure.")
    #        captcha = read.object
    #        if not captcha.checkWord(word):
    #            raise webkit.ValidationError("Captcha failure.")

    def clean(self):
        if 'passwordconfirmation' in self.cleaned_data and 'password' in self.cleaned_data \
        and self.cleaned_data['passwordconfirmation'] != self.cleaned_data['password']:
            if 'passwordconfirmation' in self._errors:
                self._errors['passwordconfirmation'].append("Passwords do not match.")
            else:
                self._errors['passwordconfirmation'] = webkit.fields.ErrorList(["Passwords do not match."])
        if 'emailconfirmation' in self.cleaned_data and 'email' in self.cleaned_data \
        and self.cleaned_data['emailconfirmation'] != self.cleaned_data['email']:
            if 'emailconfirmation' in self._errors:
                self._errors['emailconfirmation'].append("Emails do not match.")
            else:
                self._errors['emailconfirmation'] = webkit.fields.ErrorList(["Emails do not match."])
        if self._errors:
            delattr(self, 'cleaned_data')
        else:
            return self.cleaned_data


class PersonCreateManipulator(PersonManipulator):

    def buildFields(self):
        super(PersonCreateManipulator, self).buildFields()
        self.setField('name', PersonNameField())
        self.setField('passwordconfirmation', PasswordConfirmationField())
        self.setField('email', webkit.EmailField(required=True))
        #self.setField('emailconfirmation', webkit.Field(required=True))

        # Todo: Fixup captcha. Code for 0.96:
#            if self.dictionary['captcha.enable']:
#                self.fields.append(
#                    webkit.TextField(
#                        field_name="captcha", 
#                        is_required=isCaptchaEnabled, 
#                        validator_list=[
#                            self.isCaptchaCorrect
#                        ]
#                    ) 
#                )
#                self.fields.append(
#                    webkit.HiddenField(
#                        field_name="captchahash", 
#                        is_required=False,
#                    )   
#                )

    def createDomainObject(self, *args, **kwds):
        PersonManipulator.createDomainObject(self, *args, **kwds)
        if 'email' in self.data and self.domainObject:
            self.domainObject.email = self.data['email']

class PersonUpdateManipulator(PersonManipulator):

    def buildFields(self):
        super(PersonUpdateManipulator, self).buildFields()
        self.setField('passwordconfirmation', PasswordConfirmationField(required=False))
        self.setField('email', webkit.EmailField(required=True))

    def getUpdateParams(self):
        params = super(PersonUpdateManipulator, self).getUpdateParams()
        params['email'] = self.domainObject.email
        return params

    def setNonAssociateListAttributes(self):
        super(PersonUpdateManipulator, self).setNonAssociateListAttributes()
        if 'email' in self.cleaned_data:
            self.domainObject.email = self.cleaned_data['email']


