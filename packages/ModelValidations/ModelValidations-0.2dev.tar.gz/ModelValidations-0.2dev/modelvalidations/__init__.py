

class DefaultValidations(object):

    def _not_empty(self, value):
        return {'valid': True} if value and len(str(value)) > 0 else {
            'valid': False, 'message': "Can't be blank"}

    def _type_datetime(self, value):
        from datetime import datetime
        return {'valid': True} if type(value) is datetime else {
            'valid': False, 'message': "Invalid field type, should be datetime"}

    def _type_date(self, value):
        from datetime import date
        return {'valid': True} if type(value) is date else {
            'valid': False, 'message': "Invalid field type, should be date"}

    def _email(self, value):
        import re
        reg = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b', re.IGNORECASE)
        return {'valid': True} if reg.match(value) else {
            'valid': False, 'message': "Invalid email"}

    def _integer(self, value):
        import re
        reg = re.compile(r'^([-]?)([0-9]+)$')
        return {'valid': True} if reg.match(str(value)) else {
            'valid': False, 'message': "Invalid field type, should be integer"}

    def _numeric(self, value):
        import re
        reg = re.compile(r'^([-]?)([0-9]+)((.[0-9]+)?)$')
        return {'valid': True} if reg.match(str(value)) else {
            'valid': False, 'message': "Invalid field type, should be numeric"}


class ModelValidationsMetaClass(type):

    def __new__(cls, name, bases, attrs):
        clsinstance = super(ModelValidationsMetaClass, cls).__new__(
            cls, name, bases, attrs)

        if name is 'ModelValidations':
            return clsinstance

        v_methods = [m[8:] for m in attrs if m.startswith('validate')]

        clsinstance._v_methods = v_methods

        return clsinstance


class ModelValidations(object):

    __metaclass__ = ModelValidationsMetaClass

    errors = {}
    __v_cls = DefaultValidations()

    def get_v_cls(self):
        return self.__v_cls

    def _validates(self, attr, v_method):
        attr_value = getattr(self, attr)

        return getattr(self, v_method)(attr_value) if hasattr(self, v_method) \
            else getattr(self.get_v_cls(), v_method)(attr_value)

    def valid(self):
        self.errors.clear()

        for v_method in self._v_methods:
            attrs = getattr(self, 'validate%s' % v_method)

            if type(attrs) is not list:
                attrs = [attrs]

            for attr in attrs:
                validates = self._validates(attr, v_method)

                if not validates['valid']:
                    if attr in self.errors:
                        self.errors[attr].append(validates['message'])
                    else:
                        self.errors[attr] = [validates['message']]

        return False if len(self.errors) > 0 else True
