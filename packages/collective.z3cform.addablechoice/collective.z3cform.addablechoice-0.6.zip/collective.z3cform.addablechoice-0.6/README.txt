Introduction
============

This product adds a z3c.form widget (called an Addable Choice Widget) that provides a
text input in which the user can enter a new value, but also a dropdown in
which previously added values are shown.

The user therefore has the choice to use a value previously given, or to give a
new value.

When this widget is used for the first time, the dropdown will of course be
empty, as there won't be any previously added values.


How to use:
-----------

::

    from plone.directives import form
    from collective.z3cform.addablechoice.widget import AddableChoiceFieldWidget


    class IMyType(form.Schema):
        """ """
        product_name = schema.TextLine(
            title=_(u'label_product_name', default=u'Product Name'),
        )
        form.widget(product_name=AddableChoiceFieldWidget)
