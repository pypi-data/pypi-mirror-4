""" Management Plan
"""
from Products.Archetypes.atapi import ObjectField, StringField
from Products.Archetypes.Field import encode

class ManagementPlanField(StringField):
    """ Save management plan year and code
    """

    def set(self, instance, value, **kwargs):
        """
        Set management plan code and year
        """
        ObjectField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        """
        Get management plan code and year
        """
        value = ObjectField.get(self, instance, **kwargs) or ()
        data = [encode(v, instance, **kwargs) for v in value]
        return tuple(data)
