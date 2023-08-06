# This file is part of the M30W software.
# Copyright (C) 2012-2013 M30W developers.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains the Costume class.
"""
import re
from PIL import Image
import wx
import os
try:
    import kurt
except ImportError:
    pass


FORMAT_PIL = Image.Image
FORMAT_BITMAP = wx.Bitmap
FORMAT_IMAGE = wx.Image
VALID_FORMATS = (FORMAT_PIL, FORMAT_BITMAP, FORMAT_IMAGE)


def __PIL_to_wxImage(image):
    output = wx.EmptyImage(image.size[0], image.size[1])
    output.SetData(image.convert("RGB").tostring())
    output.SetAlphaData(image.convert("RGBA").tostring()[3::4])
    return output


def __wxImage_to_PIL(image):
    if not image.HasAlpha():
        image.InitAlpha()  # Avoid binary transparency

    w, h = image.GetSize()
    data = image.GetData()

    redImage = Image.new("L", (w, h))
    redImage.fromstring(data[0::3])

    greenImage = Image.new("L", (w, h))
    greenImage.fromstring(data[1::3])

    blueImage = Image.new("L", (w, h))
    blueImage.fromstring(data[2::3])

    alphaImage = Image.new("L", (w, h))
    alphaImage.fromstring(image.GetAlphaData())
    pil = Image.merge('RGBA', (redImage,
                               greenImage, blueImage, alphaImage))
    return pil


def _convert(image, format):
    """convert(image, format)

    Converts the given image object to the specified format (FORMAT_*)
    """
    # Thanks http://jehiah.cz/a/pil-to-wxbitmap,
    # http://wxpython-users.1045709.n5.nabble.com/
    # Converting-PIL-images-to-wx-Image-and-back-td2353376.html

    assert format in VALID_FORMATS, 'Invalid format!'
    assert image.__class__ in VALID_FORMATS, 'Invalid image object!'

    # Eliminating all cases where we get the image with the wanted format
    if (isinstance(image, format)):
        return image

    # Converting to wx.Image
    if isinstance(image, FORMAT_PIL):
        output = __PIL_to_wxImage(image)

    elif isinstance(image, FORMAT_BITMAP):
        output = wx.ImageFromBitmap(image)

    else:
        output = image

    if format == FORMAT_IMAGE:
        return output
    elif format == FORMAT_PIL:
        return __wxImage_to_PIL(output)
    else:
        return wx.BitmapFromImage(output)


class Costume():
    def __init__(self, image, name, center=(None, None)):
        """Costume(image, name, center=(None, None) -> new Costume object

        :param image: path or image object
        :type image: wx.Image/Bitmap, PIL.Image, path
        :param name: the costume's name
        :type name: string
        :param center: the costume's center
        :type center: tuple (x, y). None if should be middle of the image
        """

        self.name = name

        if isinstance(image, str):
            self.load_from(image)
        elif image.__class__ in VALID_FORMATS:
            self.image = _convert(image, FORMAT_PIL)
        else:
            raise TypeError("'%s' object isn't a valid image object or path"
                            % image.__class__.__name__)

        self.center = [j if j != None else self.image.size[i] // 2 for
                       i, j in enumerate(center)]  # Because center can be 0 :/

    def __getstate__(self):
        dict = self.__dict__.copy()
        image = {'pixels': self.image.tostring(),
                 'size': self.image.size,
                 'mode': self.image.mode}
        dict['image'] = image
        return dict

    def __setstate__(self, dict):
        self.__dict__ = dict
        self.image = Image.fromstring(self.image['mode'],
                                      self.image['size'],
                                      self.image['pixels'])

    def __repr__(self):
        return "<Costume %s size=%s center=%s at %s>" % (self.name,
                                                         self.size,
                                                         self.center,
                                                         id(self))

    def duplicate(self):
        match = re.match("(.*?)\(([0-9]*)\)", self.name)
        if match:
            name = match.group(1) + " (%s)" % (int(match.group(2)) + 1)
        else:
            name = self.name + " (2)"

        return Costume(self.image, name, self.center)

    @classmethod
    def from_kurt(cls, image):
        return cls(image.get_image(), image.name, image.rotationCenter.value)

    def to_kurt(self):
        image = kurt.Image.from_image(self.name, self.image)
        image.rotationCenter = kurt.Point(*self.center)
        return image

    @property
    def size(self):
        return self.image.size

    @property
    def center(self):
        return self.center

    @center.setter
    def center(self, x=0, y=0):
        self.center = (x, y)

    def save_to(self, path, type=wx.BITMAP_TYPE_PNG):
        _convert(self.image, FORMAT_IMAGE).SaveFile(path, type)

    def load_from(self, path):
        try:
            self.image = Image.open(path)
            self.image.load()
        # decoder zip not available
        except IOError:
            self.image = _convert(wx.Image(path),
                                  FORMAT_PIL)

    def get_image(self, format=wx.Bitmap):
        """get_image(self, format=wx.Bitmap) -> image object in selected format

        Returns the image object of this costume in selected format
        :param format: return type
        :type format: PIL.Image.Image | wx.Image | wx.Bitmap
        """
        return _convert(self.image, format)

    def get_thumbnail(self, size, format=wx.Bitmap):
        try:
            copy = self.image.copy()
            copy.thumbnail((size, size))
            new = Image.new('RGBA', (size, size))
            new.paste(copy, tuple([(size - i) // 2 for i in copy.size]))
            return _convert(new, format)
        # Bug on 1x1 images using Imageops.fit(), not sure if still relevant
        except ZeroDivisionError:
            copy = _convert(self.image, format=wx.Image)
            pos = [(i - size) / 2 for i in copy.GetSize()]
            return _convert(copy.Resize((size, size), pos), format)

    def get_resized_image(self, size, format=wx.Bitmap):
        """get_resized_image(self, size, format=wx.Bitmap) -> resized image
        :param size: (new width, new length)
        :type size: tuple
        :param format: return type
        :type format: PIL.Image.Image | wx.Image | wx.Bitmap
        """
        return _convert(self.image.resize(size,
                                          resample=Image.ANTIALIAS),
                        format)

def get_default_costume():
    import media
    return Costume(media.get_icon('m30w'), 'New Costume')

def get_default_background():
    return Costume(Image.new('RGB', (480, 360), '#fff'), 'New Background')