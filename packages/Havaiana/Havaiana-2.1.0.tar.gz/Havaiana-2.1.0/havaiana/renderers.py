def default_renderer(field, item, backwards=False):
    if item.required_fields is not None:
        required = field in item.required_fields
    else:
        required = False
    value = getattr(item, field)
    relation_data = item.relations.get(field)

    if backwards:
        items = []
        for element in value:
            item_ = '<a href="/%s/%s">%s</a>' % (element.plural_name,
                                                element.primary_key,
                                                element)
            items.append(item_)
        value = ", ".join(items)
        related = False
    elif value is None or relation_data is None:
        related = False
    else:
        related = "/%s/%s" % (relation_data[0].plural_name, value)
        value = relation_data[0].get(value)
        field = relation_data[1]

    if field == item.pk_field:
        field = "Primary Key (%s)" % field
    else:
        field = field.replace("_", "  ").capitalize()

    return (field, value, required, related)

def render_field(field, item, renderers, backwards=False):
    render = default_renderer
    for renderer in renderers:
        if renderer[0] == field:
            render = renderer[1]

    try:
        rendered_field = render(field, item, backwards)
    except AttributeError:
        rendered_field = (field, "", False, False)
    return rendered_field
