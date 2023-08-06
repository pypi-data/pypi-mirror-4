from django import template

### Style definition ###

class CellDesigner(object):

    DESIGNS = {}

    def register_design(self, name, func):
        CellDesigner.DESIGNS[name] = func
        
    def apply_design(self, name, value):
        if name == "":
            return value
        f = CellDesigner.DESIGNS.get(name)
        if f is None:
            raise Exception("Design '{0}' not found".format(name))
        return f(value)
        
### Decorator ###        
        
def register(func):
    name = func.__name__
    designer = CellDesigner()
    designer.register_design(name, func)
    
### Built-in ###

@register
def lower(value):
    return value.lower()
    
@register
def upper(value):
    return value.upper()
    
@register
def capitalize(value):
    return value.capitalize()       
    
@register
def bold(value):
    t = template.loader.get_template("celldesigner/bold.html")
    return t.render(template.Context({"value": value}))
    
@register
def italic(value):
    t = template.loader.get_template("celldesigner/italic.html")
    return t.render(template.Context({"value": value}))   
