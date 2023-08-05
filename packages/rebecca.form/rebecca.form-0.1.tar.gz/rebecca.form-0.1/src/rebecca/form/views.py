
import formalchemy as fa
from . import helpers as h

class FormView(object):

    FieldSet = fa.FieldSet
    __x_model__ = None
    buttons = ('submit',)
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        fs = self.create_field_set()
        self.before(fs)
        if self.can_validating():
            for button in self.buttons:
                if button in self.request.params:
                    self.before_validating(fs)
                    if fs.validate():
                        self.after_validated(fs)
                    else:
                        self.after_invalidated(fs)
        return self.template_variables(fs=fs, buttons=self.buttons)

    def template_variables(self, **kwargs):
        return kwargs

    def create_field_set(self):
        return self.FieldSet(self.__x_model__, data=self.request.params)

    def before(self, fs):
        pass

    def can_validating(self):
        return self.request.method.upper() == 'POST'

    def before_validating(self, fs):
        pass

    def after_validated(self, fs):
        pass

    def after_invalidated(self, fs):
        pass

class AddFormView(FormView):
    __x_model__ = None
    __x_session__ = None
    __x_flash_message = u"{name} created"
    def create_field_set(self):
        return self.FieldSet(model=self.__x_model__, 
            session=self.__x_session__, 
            data=self.request.params,
            request=self.request)

    def after_validated(self, fs):
        fs.sync()
        model = fs.model
        self.__x_session__.flush()
        fs.rebind(model)
        self.request.session.flash(self.__x_flash_message.format(name=h.text_(model)))

class EditFormView(FormView):
    __x_factory__ = None
    __x_flash_message = u"{name} updated"
    def create_field_set(self):
        model = self.__x_factory__(self.request)

        return self.FieldSet(model=model,
            data=self.request.params,
            request=self.request)

    def after_validated(self, fs):
        fs.sync()
        model = fs.model
        self.request.session.flash(self.__x_flash_message.format(name=h.text_(model)))

class DisplayView(FormView):
    __x_factory__ = None
    def create_field_set(self):
        model = self.__x_factory__(self.request)

        fs = self.FieldSet(model=model,
            data=self.request.params,
            request=self.request)
        return fs

    def before(self, fs):
        fs.configure(readonly=True)

    def can_validating(self):
        return False