rebecca.form
====================

`pyramid <http://pypi.python.org/pyramid>`_ view components based on `FormAlchemy <http://pypi.python.org/Formalchemy>`_ .

Components
-------------------

- FormView
- AddFormView
- EditFormView
- DisplayView


Examples
--------------------

Model for Example ::

    class Item(Base):
        __tablename__ = 'items'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.Unicode(255), nullable=False)
        value = sa.Column(sa.Integer, nullable=False)

        def __unicode__(self):
            return u"Item id={id}, name={name}, value={value}".format(id=self.id, name=self.name, value=self.value)

AddFormView ::

    class AddItemView(AddFormView):
        __x_model__ = Item
        __x_session__ = DBSession

EditFormView ::

    class EditItemView(EditFormView):
        __x_factory__ = item_finder

DisplayView ::

    class DisplayItemView(DisplayView):
        __x_factory__ = item_finder

`__x_factory__` is callable to find model from request.

Utilities
----------------------

`MatchDictFinder` queries for specified Model with conditions from `Request.matchdict`.

For example, create finder for ::

    item_finder = MatchDictFinder(Item, DBSession, [(Item.id, 'item_id')])

item_finder executes like this ::

    DBSession.query(Item).filter(Item.id==request.matchdict['item_id']).one()

