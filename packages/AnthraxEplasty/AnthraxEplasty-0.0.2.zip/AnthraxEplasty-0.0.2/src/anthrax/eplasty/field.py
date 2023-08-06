from anthrax.field.base import Field
from anthrax.exc import ValidationError

class UniqueMixin(Field):
    """Fields that contain this mixin require during a validation to have
    unique value if the form mode is ADD. They are used to reflect unique
    fields (like slugs)."""

    def __init__(self, *args, **kwargs):
        self.EpClass = kwargs.pop('EPClass')
        self.ep_field = kwargs.pop('ep_field')
        super(UniqueMixin, self).__init__(*args, **kwargs)

    def validate_python(self, value, bf):
        # If we modify an existing object and don't change the value
        # It is ok. Otherwise check if we don't violate unique
        if not (
            hasattr(bf.form, 'object_') and
            getattr(bf.form.object_, self.ep_field.name) == value
        ):
            existing = self.EpClass.find(
                self.ep_field == value, session = bf.form.ep_session)
            if list(existing):
                raise ValidationError('Value exists')
