def htmlise(obj):
    if isinstance(obj, dict):
        return dict_html(obj)
    if isinstance(obj, (list, set, tuple)):
        return list_html(obj)
    return str(obj)

_dict_html_template = "<ul>{}</ul>"
_item_html_template = "<li><strong>{}:</strong> {}</li>"

def dict_html(d):
    items = (_item_html_template.format(str(k), htmlise(v)) for k,v in d.items())
    return _dict_html_template.format("\n".join(items))
        
def list_html(l):
    return ", ".join(l)
