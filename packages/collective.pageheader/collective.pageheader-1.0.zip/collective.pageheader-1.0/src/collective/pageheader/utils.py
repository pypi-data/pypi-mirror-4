from collective.pageheader.extenders import PAGEHEADER_FIELDNAME


def get_pageheader_image(context):
    field = context.getField(PAGEHEADER_FIELDNAME)
    return field and field.get(context) or None
