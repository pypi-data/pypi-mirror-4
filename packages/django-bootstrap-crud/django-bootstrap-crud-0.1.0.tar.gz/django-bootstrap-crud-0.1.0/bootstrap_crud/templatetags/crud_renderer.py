from django import template
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from ruymossi.celldesigner import designer

register = template.Library()

### Messages ###

ERROR_ID_NOT_FOUND = _("Object with id {0} was not found")
ERROR_EXCEPTION = _("The following error has ocurred: {0}")

SUCCESS_OPERATION = _("Operation successfully done")

### Helper Functions ###

def get_attr_value(obj, attr_name):
    attrs = attr_name.split(".")
    for attr in attrs:
        obj = getattr(obj, attr)
    return obj

### Filters ###

@register.filter
def get_attribute(obj, column):
    return get_attr_value(obj, column)
    
@register.filter
def apply_design(value, names):
    names = names.lower().split("|")
    d = designer.CellDesigner()
    for name in names:
        value = d.apply_design(name, value)
    return value

@register.filter
def apply_css(manager, obj):
    return manager.get_css_class(obj)

@register.filter
def crud(obj):
    template_name, context = obj.get_action()
    t = template.loader.get_template(template_name)
    return t.render(template.RequestContext(obj.request, context))

### Classes ###

class Action(object):
    
    def __init__(self, opt, caption):
        self.opt = opt
        self.caption = caption

    def get_action(self, owner, post_data=None):
        return ("", {})

class ErrorAction(Action):

    def __init__(self, message=""):
        Action.__init__(self, "error", "")
        self.message = message

    def get_action(self, owner, post_data=None):
        return ("crud/crud_error.html", {"error_message": self.message, "list_url": owner.url})
        
class SuccessAction(Action):

    def __init__(self, message=""):
        Action.__init__(self, "success", "")
        self.message = message

    def get_action(self, owner, post_data=None):
        return ("crud/crud_success.html", {"success_message": self.message, "list_url": owner.url})        
        
class ListObjectAction(Action):

    def __init__(self):
        Action.__init__(self, "__default__", "")
        self.elements = []
        self.columns = []
        self.header_designs = ""
            
    def add_column(self, attr, designs="", header=""):
        if header == "":
            header = attr.replace("_", " ").capitalize()
        self.columns.append((attr, designs, header))

    def get_css_class(self, obj):
        return ""   

    def get_action(self, owner, post_data=None):
        self.elements = owner.get_all()
        paginator = Paginator(self.elements, 10)    
        page = owner.request.GET.get("page")
        try:
            self.elements = paginator.page(page)
        except:
            self.elements = paginator.page(1)
        return ("crud/crud_list.html", {"action": self, "form_url": owner.url, "global_actions": owner.global_actions, "row_actions": owner.row_actions})

class NewObjectAction(Action):

    def __init__(self, opt, caption, form_class):
        Action.__init__(self, opt, caption)
        self.FormClass = form_class

    def get_action(self, owner, post_data=None):
        form = self.FormClass()
        if post_data is not None:
            form = self.FormClass(post_data)
            if form.is_valid():
                owner.save(form.cleaned_data)
                return SuccessAction(message=SUCCESS_OPERATION).get_action(owner)
        return ("crud/crud_edit.html", {"form": form, "form_url": owner.url, "crud_id": owner.crud_id, "crud_opt": self.opt})

class EditObjectAction(Action):

    def __init__(self, opt, caption, form_class, form_mapping={}):
        Action.__init__(self, opt, caption)
        self.FormClass = form_class
        self.form_mapping = form_mapping

    def get_action(self, owner, post_data=None):
        obj = owner.get_by_id(owner.crud_id)
        if obj == None:
            return ErrorAction(message=ERROR_ID_NOT_FOUND.format(owner.crud_id)).get_action(owner)
        form = self.FormClass()
        if post_data is not None:
            form = self.FormClass(owner.request.POST)
            if form.is_valid():
                owner.save(form.cleaned_data, owner.crud_id)
                return SuccessAction(message=SUCCESS_OPERATION).get_action(owner)
        else:     
            m = {}
            for key in self.form_mapping:
                value = get_attr_value(obj, self.form_mapping[key])
                m[key] = value
            form = self.FormClass(initial=m)
        return ("crud/crud_edit.html", {"form": form, "form_url": owner.url, "crud_id": owner.crud_id, "crud_opt": self.opt})

class RemoveObjectAction(Action):

    def __init__(self, opt, caption):
        Action.__init__(self, opt, caption)

    def get_action(self, owner, post_data=None):
        obj = owner.get_by_id(owner.crud_id)
        if obj == None:
            return ErrorAction(message=ERROR_ID_NOT_FOUND.format(owner.crud_id)).get_action(owner)
        if post_data is not None:
            owner.delete(owner.crud_id)
            return SuccessAction(message=SUCCESS_OPERATION).get_action(owner)
        return ("crud/crud_remove.html", {"form_url": owner.url, "crud_id": owner.crud_id, "crud_opt": self.opt})
        
class ActionManager(object):

    def __init__(self, request, *args):
        self.url = "#"
        self.request = request

        self.crud_opt = None
        self.crud_id = None
        if len(args) > 0:
            if args[0] != "":
                self.crud_opt = args[0] 
        if len(args) == 2:
            self.crud_id = args[1]

        self.default_action = None
        self.global_actions = []
        self.row_actions = []

    def add_global_action(self, action):
        self.global_actions.append(action)

    def add_row_action(self, action):
        self.row_actions.append(action)
        
    def get_all(self):
        return [] 

    def delete(self, id):
        pass

    def save(self, data, id=None):
        pass

    def get_by_id(self, id):
        return None

    def get_action(self):
        try:
            actions = self.global_actions + self.row_actions

            post_data = None
            if self.request.method == "POST":
                post_data = self.request.POST

            for action in actions:
                if self.crud_opt == action.opt:
                    return action.get_action(self, post_data)
            return self.default_action.get_action(self, post_data)

        except Exception, e:
            return ErrorAction(message=ERROR_EXCEPTION.format(e.message)).get_action(self)
