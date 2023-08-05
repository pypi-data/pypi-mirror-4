"""Contains the Costume class.
"""
from PIL import Image
import wx
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
    #Thanks http://jehiah.cz/a/pil-to-wxbitmap,
    #http://wxpython-users.1045709.n5.nabble.com/
    #Converting-PIL-images-to-wx-Image-and-back-td2353376.html

    assert format in VALID_FORMATS, 'Invalid format!'
    assert image.__class__ in VALID_FORMATS, 'Invalid image object!'

    #Eliminating all cases where we get the image with the wanted format
    if (isinstance(image, format)):
        return image

    #Converting to wx.Image
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
    def __init__(self, image, name, center=(0, 0)):
        """Costume(image, name, center=(0, 0) -> new Costume object

        :param image: path or image object
        :type image: wx.Image/Bitmap, PIL.Image, path
        :param name: the costume's name
        :type name: string
        :param center: the costume's center
        :type center: tuple (x, y)
        """

        self.name = name
        self.center = center

        if isinstance(image, str):
            self.image = Image.open(image)
        elif image.__class__ in VALID_FORMATS:
            self.image = _convert(image, FORMAT_PIL)
        else:
            raise TypeError("'%s' object isn't a valid image object or path"
                            % image.__class__.__name__)

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
    @classmethod
    def from_kurt(cls, image):
        return cls(image.get_image(), image.name, image.rotationCenter.value)

    def to_kurt(self):
        image = kurt.Image.from_image(self.name, self.image)
        image.rotationCenter = kurt.Point(*self.center)
        return image

    def get_size(self):
        return self.image.size

    def get_center(self):
        return self.center

    def set_center(self, x=0, y=0):
        """set_center(self, x, y)

        Sets the costume center.
        :param x: new center x
        :type x: int
        :param y: new center y
        :type y: int
        """
        self.center = (x, y)

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
        #Bug on 1x1 images using Imageops.fit(), not sure if still relevant
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

DEFAULT_COSTUME = Costume(Image.new('RGB', (480, 360), '#fff'), 'New Costume')
