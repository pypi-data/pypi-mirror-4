#-*- coding: utf-8 -*-
''' Extended class of ImageField.
    It can add previews by set sizes and sort them to directories.
    It use self.storage for all operations with files
    It used widget with thumbnail in admin interface
    It also can retrun a dictonary (height, width, url) of preview's name in the template '''

import cStringIO
import os

from PIL import Image
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile

from .widgets import ExtendedImageWidget
from .utils import gen_filename


class ExtendedImageFieldFile(ImageFieldFile):
    def __init__(self, *args, **kwargs):
        super(ExtendedImageFieldFile, self).__init__(*args, **kwargs)
        for preview in self.field.previews:
            setattr(self, preview['name'], self.get_thumb_params(preview['name']))

    def save(self, name, content, save=True):
        name = gen_filename(name)
        if self.instance.pk:
            model = self.field.model
            try:
                old_image = model.objects.get(pk=self.instance.pk)
                old_path = getattr(old_image, self.field.attname)
                if self.storage.exists(old_path):
                    self.storage.delete(old_path)
                self.delete_previews(old_path.name)
            except model.DoesNotExist:
                pass
        super(ExtendedImageFieldFile, self).save(name, content, save)
        self.add_previews(name, content)

    def delete(self, save=True):
        self.delete_previews(self.name)
        super(ExtendedImageFieldFile, self).delete(save)

    def add_previews(self, name, content):
        ext = os.path.splitext(name)[-1]
        image_name = os.path.basename(name).replace(ext, '')
        image_dir = os.path.dirname(self.storage.path(name))

        content.seek(0)
        image = Image.open(content).convert('RGBA')
        for preview in self.field.previews:
            out = cStringIO.StringIO()
            newdir = os.path.join(image_dir, self.field.upload_to, preview['name'])
            if self.field.dir_sort and not os.path.isdir(newdir):
                try:
                    os.makedirs(newdir)
                except OSError:
                    self.field.dir_sort = False

            preview_path = self.get_preview_path(preview['name'], image_name, ext.lower())
            width = preview['width'] if 'width' in preview else \
                float(image.size[0]) * (preview['height'] / float(image.size[1]))
            height = preview['height'] if 'height' in preview else \
                float(image.size[1]) * (preview['width'] / float(image.size[0]))

            preview_file = image.resize((int(round(width)), int(round(height))), Image.ANTIALIAS)
            preview_file.save(out, ext.lstrip('.').lower().replace('jpg', 'jpeg'))
            self.storage.save(preview_path, ContentFile(out.getvalue()))

    def delete_previews(self, name):
        ext = os.path.splitext(name)[-1]
        image_name = os.path.basename(name).replace(ext, '')

        for preview in self.field.previews:
            preview_path = self.get_preview_path(preview['name'], image_name, ext)
            if self.storage.exists(preview_path):
                self.storage.delete(preview_path)

    def get_preview_path(self, thumb_name, file_name, ext):
        if self.field.dir_sort:
            preview_path = os.path.join(
                self.field.upload_to, thumb_name, '%s%s' % (file_name, ext))
        else:
            preview_path = os.path.join(
                self.field.upload_to, '%s_%s%s' % (file_name, thumb_name, ext))
        return preview_path

    def get_thumb_params(self, thumb_name):
        empty = {'width': 0, 'height': 0, 'url': ''}
        if not self.name:
            return empty

        ext = os.path.splitext(self.name)[-1]
        preview_name = os.path.basename(self.name).replace(ext, '')

        if self.field.dir_sort:
            preview_path = os.path.join(
                self.field.upload_to, thumb_name, '%s%s' % (preview_name, ext))
        else:
            preview_path = os.path.join(
                self.field.upload_to, '%s_%s%s' % (preview_name, thumb_name, ext))

        if self.storage.exists(preview_path):
            preview = Image.open(self.storage.path(preview_path))
            preview_dict = {
                'width': preview.size[0],
                'height': preview.size[1],
                'url': self.storage.url(preview_path)}
            return preview_dict
        return empty


class ExtendedImageField(ImageField):
    '''
    Set attribute preview to tuple of dictonaries contains:
    name - required. Name of preview.
    width - preview's width. If not set it will calculate from
            height on the basis of proportions
    height - preview's height. If not set it will calculate from
            width on the basis of proportions
    Set attribute dir_sort to True is you want to sort your previews to folders
    Set attribute widget_preview to name of preview you want to show in admin widget
    If widget_preview is not set - uploaded image will be shown in admin widget
    Also you can pass yours own widget as widget arg
    '''
    attr_class = ExtendedImageFieldFile

    def __init__(self, previews=None, dir_sort=True, widget=None, widget_preview=None, **kwargs):
        self.previews = previews
        self.dir_sort = dir_sort
        self.widget = widget

        if self.widget is None:
            preview = widget_preview or 'self'
            self.widget = ExtendedImageWidget(attrs={'preview': preview})
        super(ExtendedImageField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = self.widget
        return super(ExtendedImageField, self).formfield(**kwargs)
