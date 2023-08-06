from .. ordereddict import OrderedDict

from mako.template import Template
from mako.lookup import TemplateLookup

from os import path

htmlTemplateLookup = TemplateLookup ( directories = [ path.join(path.dirname(path.abspath(__file__)), "templates/html/") ] )

class XWidget(object):
    creation_counter = 0
    template_name = "base"
    is_hidden = False
    
    def __init__(self, data_id="_default_", **kkw):
        XWidget.creation_counter += 1
        self.creation_counter = XWidget.creation_counter
        self.data_id = data_id                

    def to_unicode(self, v):
        return unicode(v)

    def to_python(self, v):
        return v

    def html(self, field):
        return htmlTemplateLookup.get_template ( "{1}.{0}.html".format(self.template_name, self.__class__.__name__.lower()) ).render_unicode(widget=self, field=field)

    def __repr__(self):        
        return "<{0.__class__.__name__} ({0.data_id}) #{0.creation_counter}>".format(self)

class XWidgetHidden(XWidget):
    is_hidden = True

def get_base_widgets(bases, attrs):
    excluded = attrs.get ( 'excluded', tuple() )
    
    widgets = [ ( data_id, attrs.pop(data_id) ) for data_id, obj in attrs.items() if isinstance(attrs[data_id], XWidget) ]
    widgets.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))
    for (data_id, w) in widgets: w.data_id = data_id

    for base in bases[::-1]:
        if hasattr(base, 'declared_widgets'): 
            widgets = widgets + base.declared_widgets.items()
        if hasattr(base, "excluded"):
            excluded = excluded + base.excluded
    widgets = OrderedDict(widgets)
    for exc in excluded: widgets.pop(exc, None)

    return widgets

class DeclarativeXLayout(type):
    def __new__(cls, name, bases, attrs):
        attrs['declared_widgets'] = get_base_widgets(bases, attrs)
        return type.__new__ (cls, name, bases, attrs)

class XField(object):
    def __init__(self, layout, data_id):
        self.layout = layout
        self.data_id = data_id
        self._buffer = u""

    def _get_widget(self):
        return self.layout.get_widget(self.data_id)
    widget = property(_get_widget)
    
    def _set_value(self, value):
        self.buffer = self.widget.to_unicode(value)
    def _get_value(self):
        return self.widget.to_python(self.buffer)
    value = property(_get_value, _set_value)
 
    def _get_buffer(self):
        return self._buffer
    def _set_buffer(self, buffer):
        self._buffer = buffer
    buffer = property(_get_buffer, _set_buffer)

    def _get_label(self):
        return self.data_id
    label = property(_get_label)

    def __repr__(self):
        return "<{0.__class__.__name__} ({0.data_id}) {0.widget}>".format(self)

class XLayoutRenderer(object):
    def __init__(self, layout):
        self.layout = layout
    
    def render(self):
        raise NotImplementedError

class XLayoutHTMLRenderer(XLayoutRenderer):
    template_name = "base"

    def render(self):
        return htmlTemplateLookup.get_template ( "xform.{0}.html".format(self.template_name) ).render_unicode(form=self.layout.form)

class XLayoutBase(object):
    template_name = "base"
    default_renderer = XLayoutHTMLRenderer

    def __init__(self, form, **kkw):
        self.fields = OrderedDict()
        self.form = form
        self.renderer = kkw.get("renderer_class", self.default_renderer) (self)
        for data_id, w in self.declared_widgets.items():
            self.fields[w.data_id] = XField(self, w.data_id)
    
    def get_widget(self, data_id):
        return self.declared_widgets[data_id]

    def __iter__(self):
        for data_id, f in self.fields.items():
            yield f

    def __getitem__(self, key):
        return self.fields[key]

    def render(self):
        return self.renderer.render()

class XLayout(XLayoutBase):
    __metaclass__ = DeclarativeXLayout

def XLayoutForSchema(schema, BaseLayout = XLayout):
    class XLayoutSchema(BaseLayout):
        class __metaclass__(BaseLayout.__metaclass__):
            def __new__(cls, name, bases, attrs):
                cr = list(schema.columns())
                cr.reverse()
                for c in cr:
                    attrs[c.COLUMN_NAME] = XWidget (c.COLUMN_NAME)

                return BaseLayout.__metaclass__.__new__(cls, name, bases, attrs)
    XLayoutSchema.__name__ = "XLayout_" + schema.name
    return XLayoutSchema



class XForm(object):
    layout_class = XLayout
    template_name = "base"

    def __init__(self, **kkw):
        layout_class = kkw.get ( "layout_class", self.layout_class )        
        self.layout = layout_class(self)

    def __getitem__(self, key):
        return self.layout[key].value

    def __setitem__(self, key, value):
        self.layout[key].value = value

    def feed(self, data):
        for k,v in data.items(): self[k] = v

    def __iter__(self):
        for k in self.layout:
            yield k
    
class XRecordForm(XForm):
    
    def __init__(self, db, table_name, **kkw):
        if hasattr(self, 'Layout'): customBase = self.Layout
        else: customBase = XLayout
        self.layout_class = XLayoutForSchema( db.XSchema(table_name), customBase )
        self.table_name = table_name        
        XForm.__init__(self, **kkw)
        self._record = None

    def _get_record(self):
        return self._record

    def _set_record(self, record):
        self._record = record
        for f in self.layout:
            if f.data_id in record:
                f.value = record[f.data_id]    
    record = property(_get_record, _set_record)

    def __setitem__(self, key, value):
        super(XRecordForm, self).__setitem__(key, value)
        if key in self.record:
            self.record[key] = value

def XRecordFormsCache(db):
    class forms_cache:
        def __init__(self):
            self.cache = {}
        def __getattr__(self, attr):
            if attr not in self.cache:
                class aForm(XRecordForm):
                    def __init__(self):
                        XRecordForm.__init__(self, db, attr)
                    pass
                aForm.__name__ = attr + '_form'
                self.cache[attr] = aForm
            return self.cache[attr]
        
        def __setitem__(self, key, item):
            self.cache[key] = item

        def __call__(self, cls):
            self.cache[cls.__name__] = cls
            return cls

    return forms_cache()
