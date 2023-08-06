from anthrax.field.action import Action

def create_object(Type, form):
    values = dict()
    for k, v in form.items():
        if isinstance(form.__fields__[k]._field, Action):
            continue
        else:
            values[k] = v
            
    return Type(**values)

def load_form(obj, form):
    form.object_ = obj
    for k, v in form.__fields__.items():
        val = getattr(obj, k, None)
        if val is not None:
            form[k] = val

def update_object(obj, form):
    for k, v in form.items():
        if isinstance(form.__fields__[k]._field, Action):
            continue
        else:
            try:
                setattr(obj, k, v)
            except TypeError:
                if getattr(obj, k) != v:
                    raise ValueError('This form belongs to another object!')
