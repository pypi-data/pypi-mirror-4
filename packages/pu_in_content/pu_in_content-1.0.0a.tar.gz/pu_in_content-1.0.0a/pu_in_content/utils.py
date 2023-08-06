def convert_imageattachment(field):

    img = field.field.to_python(field.value())

    if img:
        return """<img src="%s"/>""" % img.get_profile_middle_url()
    else:
        return ""

def convert_nothing(field):

              return field.value()


CONVERTERS = {'SingleImageAttachmentField':
                  convert_imageattachment}


def value_to_html(field):

    converter = CONVERTERS.get(field.field.__class__.__name__, convert_nothing)

    return converter(field)
