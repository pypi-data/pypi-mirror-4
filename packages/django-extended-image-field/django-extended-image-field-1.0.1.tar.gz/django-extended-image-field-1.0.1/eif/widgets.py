from django.forms.widgets import FileInput
from django.utils.safestring import mark_safe


class ExtendedImageWidget(FileInput):
    def __init__(self, attrs=None):
        super(ExtendedImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if not self.attrs is None:
            preview_name = self.attrs['preview']
            if preview_name == 'self' and hasattr(value, 'url'):
                output.append(('<br /><br /><a target="_blank" href="%s">'
                           '<img src="%s" style="height: %dpx; width=%dpx;" /></a><br /> '
                           % (value.url, value.url, value.height, value.width)))
            elif value and hasattr(value, preview_name):
                preview = getattr(value, preview_name)
                output.append(('<br /><br /><a target="_blank" href="%s">'
                           '<img src="%s" style="height: %dpx; width=%dpx;" /></a><br /> '
                           % (value.url, preview['url'], preview['height'], preview['width'])))
        output.append(super(ExtendedImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
