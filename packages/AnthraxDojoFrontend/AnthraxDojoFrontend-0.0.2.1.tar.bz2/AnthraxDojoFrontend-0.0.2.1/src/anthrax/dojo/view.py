import tempfile
import pkg_resources as pr

import mako.lookup

from anthrax.dojo import view_helpers

LOOKUP = mako.lookup.TemplateLookup(directories=[
    pr.resource_filename('anthrax.dojo', '/templates')
], module_directory=tempfile.mkdtemp())


class SimpleDojoView():
    lookup = LOOKUP

    def __init__(self, require, template_name, **kwargs):
        self.require = require
        self.template_name = template_name
        self.kwargs = kwargs

    def __call__(self, **kwargs):
        kwargs['h'] = view_helpers
        kwargs.update(self.kwargs)
        return (
            self.require,
            self.lookup.get_template(self.template_name).render(**kwargs)
        )

anthrax_text_box_view = SimpleDojoView(
    'anthrax/js/AnthraxTextBox', 'anthrax_text_box.mako', input_type='text'
)
anthrax_password_box_view = SimpleDojoView(
    'anthrax/js/AnthraxTextBox', 'anthrax_text_box.mako', input_type='password'
)
textarea = SimpleDojoView('dijit/form/Textarea', 'textarea.mako')
spinner_view = SimpleDojoView('dijit/form/NumberSpinner', 'spinner.mako')
editor = SimpleDojoView('dijit/Editor', 'editor.mako')
hidden = SimpleDojoView(None, 'hidden.mako')
datebox = SimpleDojoView('anthrax/js/AnthraxDateBox', 'anthrax_datebox.mako')
button = SimpleDojoView('dijit/form/Button', 'button.mako')
file_upload = SimpleDojoView('dojox/form/Uploader', 'file_upload.mako')

def html_tabular_form_view(form):
    return LOOKUP.get_template('tabular_form.mako').render(
        form=form, h=view_helpers
    )
