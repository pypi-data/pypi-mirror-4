from collections import OrderedDict

from eplasty.object.base import Object
from eplasty.object.meta import ObjectMeta
from eplasty.field.simple import Integer, CharacterVarying, Text, Date, Array
from eplasty.field.helper import SimplePK
from eplasty.field.adapter import Html
from eplasty.field.blob import Blob
from eplasty.field.image import Image

from anthrax.util import bind_fields
from anthrax.reflector import Reflector
from anthrax.field import IntegerField, TextField, DateField, ListField
from anthrax.field import FileField
from anthrax.widget import Hidden, TextInput, LongTextInput
from anthrax.html_input.field import HtmlField

EDIT = 'EDIT'

class EplastyReflector(Reflector):

    def get_fields(self, form):
        if not isinstance(self.source, (Object, ObjectMeta)):
            raise TypeError('The reflection source must be Elephantoplasty'
                'Object or Object class')
        result = OrderedDict()
        for field in self.source.fields:
            anthrax_field = self._handle_field(field)
            if anthrax_field is not None:
                result[field.name] = anthrax_field
        bind_fields(result, form)
        return result

    def _handle_field(self, field):
        dispatcher = self._map.get(type(field))
        if dispatcher:
            return getattr(self, dispatcher)(field)

    def _simple_pk_handler(self, field):
        return IntegerField(widgets=[Hidden], mode=EDIT)

    def _integer_handler(self, field):
        return IntegerField()

    def _varchar_handler(self, field):
        return TextField()

    def _text_handler(self, field):
        return TextField(widgets=[LongTextInput, TextInput])

    def _date_handler(self, field):
        return DateField()

    def _html_handler(self, field):
        return HtmlField()

    def _array_handler(self, field):
        subfield = self._handle_field(field.itemtype)
        return ListField(subfield=subfield)

    def _file_handler(self, field):
        return FileField()

    def _image_handler(self, field):
        try:
            from anthrax.image.field import ImageField
            return ImageField()
        except ImportError:
            return FileField()

    _map = {
        SimplePK: '_simple_pk_handler',
        Integer: '_integer_handler',
        CharacterVarying: '_varchar_handler',
        Text: '_text_handler',
        Date: '_date_handler',
        Html: '_html_handler', 
        Array: '_array_handler',
        Blob: '_file_handler',
        Image: '_image_handler',
    }
