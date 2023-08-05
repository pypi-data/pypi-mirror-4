import inspect, time
import tg
from tg.decorators import Decoration, expose
from webhelpers.html import HTML

try:
    import json
except:
    import simplejson as json

from tw_compat import TW1, TW2, is_tw2_form, inject_widget_resources, form_class_name

def ajaxloaded(decorated):
    def display(w, value={}, **kw):
        inject_widget_resources(w)

        form_id = form_class_name(w)
        return HTML(HTML.div('', id=form_id), 
                    HTML.script(HTML.literal('''jQuery(document).ready(function() {{
jQuery('#{0}').load('{1}', {2});
}});'''.format(form_id, w.ajaxurl, json.dumps(value)))))

    def on_demand(w):
        inject_widget_resources(w)

        form_id = form_class_name(w)
        return HTML(HTML.script(HTML.literal('''\
function {0}_on_demand(where, params) {{
    jQuery(where).load('{1}', params);
}};'''.format(form_id, w.ajaxurl))))

    if hasattr(decorated, '_ajaxform_display'):
        raise RuntimeError('Form you are trying to decorate with ajaxloaded seems to be already an ajaxloaded form')

    decorated._ajaxform_display = decorated.display

    if is_tw2_form(decorated):
        decorated.resources.extend([TW2.jquery_js, TW2.jquery_form_js])
        decorated.display = classmethod(display)
        decorated.on_demand = classmethod(on_demand)
    else:
        decorated.javascript.extend([TW1.jquery_js, TW1.jquery_form_js])
        decorated.display = display
        decorated.on_demand = on_demand
    return decorated

class formexpose(object):
    def __init__(self, arg, template='tgext.ajaxforms.templates.ajaxform'):
        if inspect.isclass(arg):
            self.form = arg()
        else:
            self.form = arg
        self.template = template

    def decorate_func(self, decorated):
        def before_render(remainder, params, output):
            output['ajaxform'] = self.form
            output['ajaxform_id'] = "%s_loaded_%s" % (form_class_name(self.form), int(time.time()*1000))
            output['ajaxform_action'] = self.form.action

            if is_tw2_form(self.form):
                output['ajaxform_spinner'] = TW2.spinner_icon.req()
                output['ajaxform_spinner'].prepare()
            else:
                output['ajaxform_spinner'] = TW1.spinner_icon

            if not output.has_key('value'):
                output['value'] = {}

        decorated = expose(self.template)(decorated)
        decoration = Decoration.get_decoration(decorated)
        decoration.register_hook('before_render', before_render)
        return decorated

    def __call__(self, decorated):
        return self.decorate_func(decorated)

def ajaxform(arg):
    def real_method(self, *args, **kw):
        return dict(value=kw)
    
    return formexpose(arg)(real_method)

