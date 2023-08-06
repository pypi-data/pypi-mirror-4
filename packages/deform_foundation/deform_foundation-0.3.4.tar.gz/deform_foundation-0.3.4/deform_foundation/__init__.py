import colander
import deform.widget

from pkg_resources import resource_filename

from deform import Form

from .resources import default_resources

@colander.deferred
def deferred_csrf_value(node, kw):
    return kw['request'].session.get_csrf_token()

@colander.deferred
def deferred_csrf_validator(node, kw):
    def csrf_validate(node, value):
        if value != kw['request'].session.get_csrf_token():
            raise colander.Invalid(node, 'Invalid cross-site scripting token')
    return csrf_validate

class CSRFSchema(colander.Schema):
    """
    Schema base class which generates and validates a CSRF token
    automatically.  You must use it like so:

    .. code-block:: python

      from pyramid_deform import CSRFSchema
      import colander

      class MySchema(CRSFSchema):
          my_value = colander.SchemaNode(colander.String())

      And in your application code, *bind* the schema, passing the request
      as a keyword argument:

      .. code-block:: python

        def aview(request):
            schema = MySchema().bind(request=request)

      In order for the CRSFSchema to work, you must configure a *session
      factory* in your Pyramid application.
    """
    csrf_token = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        default=deferred_csrf_value,
        validator=deferred_csrf_validator,
        )

def add_resources_to_registry():
    """Register deform_foundation widget specific requirements to
       deform's default resource registry
    """
    registry = Form.default_resource_registry
    for rqrt, versions in default_resources.items():
        for version, resources in versions.items():
            registry.set_js_resources(rqrt, version, resources.get('js'))
            registry.set_css_resources(rqrt, version, resources.get('css'))

def add_search_path():
    search_path = (resource_filename('deform_foundation', 'templates'), resource_filename('deform', 'templates'))
    
    Form.set_zpt_renderer(search_path)

def includeme(config):
    add_search_path()
    add_resources_to_registry()
    config.add_static_view('static-deform_foundation', 'deform_foundation:static')
