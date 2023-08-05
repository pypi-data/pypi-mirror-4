""" Reference field
"""
from Products.validation import ValidationChain
from Products.Archetypes.atapi import ReferenceField

class EEAReferenceField(ReferenceField):
    """ Customize ReferenceBrowser field
    """
    def validate_relations(self, value, instance, errors=None, **kwargs):
        """ Validate relations
        """
        chainname = 'Validator_%s' % self.getName()
        validators = ValidationChain(chainname,
                                     validators=('eea.relations.required',))
        result = validators(value, instance=instance,
                            errors=errors, field=self, **kwargs)
        if result is not True:
            return result
        return None

    def validate(self, value, instance, errors=None, **kwargs):
        """ Validate passed-in value using all field validators.
            Return None if all validations pass; otherwise, return failed
            result returned by validator
        """
        if errors is None:
            errors = {}
        res = self.validate_relations(value, instance, errors, **kwargs)
        if res is not None:
            return res
        return super(EEAReferenceField, self).validate(
            value, instance, errors=None, **kwargs)
