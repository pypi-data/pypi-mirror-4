"""
This defines the classes returned by the API.

Oh you were expecting Django models...that's cute.
"""


class BaseHeathcareObject(dict):
    """
    Common API functionality for healthcare models.
    It's a dictionary with some additional functionality.
    """

    fields = ()

    def __getattr__(self, name):
        if name in self.__class__.fields:
            return self.get(name, None)
        else:
            return dict.__getattribute__(self, name)


class Patient(BaseHeathcareObject):
    "A patient record from the API."

    fields = (
        'id', 'name', 'sex', 'birth_date', 'death_date', 'status',
        'created_date', 'updated_date', 'location'
    )


class Patient(BaseHeathcareObject):
    "A provider record from the API."

    fields = (
        'id', 'name', 'status', 'created_date', 'updated_date', 'location'
    )
