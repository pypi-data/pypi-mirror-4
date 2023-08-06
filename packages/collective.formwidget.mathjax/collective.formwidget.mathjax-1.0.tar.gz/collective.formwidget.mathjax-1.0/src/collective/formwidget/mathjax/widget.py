import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget
from z3c.form.browser.textarea import TextAreaWidget

from collective.formwidget.mathjax.interfaces import IMathJaxWidget

class MathJaxWidget(TextAreaWidget):
    """MathJax widget implementation."""
    zope.interface.implementsOnly(IMathJaxWidget)

    klass = u'mathjax-widget'
    value = u''

    def update(self):
        super(MathJaxWidget, self).update()
        widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def MathJaxFieldWidget(field, request):
    """IFieldWidget factory for MathJaxWidget."""
    return FieldWidget(field, MathJaxWidget(request))

