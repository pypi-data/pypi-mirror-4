from nib import jinja

@jinja('filter')
def itemfilter(items, attrs=None):
    if hasattr:
        if type(attrs) != list:
            attrs = list(attrs)
        for attr in attrs:
            items = filter(lambda i: hasattr(i, attr), items)
    return items
