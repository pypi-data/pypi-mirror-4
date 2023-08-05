#forms.py
import wtforms
from utils import MultiValueDict
from wtforms.compat import iteritems

class Form(wtforms.Form):

    def __init__(self, handler=None, **kwargs):
        formdata = MultiValueDict()
        if handler:
            for name in handler.request.arguments.keys():
                formdata.setlist(name, handler.get_arguments(name))
            
            # we should also iterate over request.files because
            # get_arguments does not return list of filenames
            for field, files in iteritems(handler.request.files):
                names = []
                for file in files:
                    names.append(file['filename'])
                formdata.setlist(field, names)
        super(Form, self).__init__(formdata, **kwargs)