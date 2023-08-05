import unittest
from pyramid import testing
from formalchemy import Field
from sqlalchemy import types

class DummySchema(object):
    name = Field()
    value = Field(type=types.Integer)

class FormViewTests(unittest.TestCase):
    def _getTarget(self):
        from .views import FormView
        return FormView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()

        target = self._makeOne(context, request)
        target.__x_model__ = DummySchema

        result = target.create_field_set()

        self.assertEqual(result.name.value, None)
        self.assertEqual(result.value.value, None)
