# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.db.models.loading import get_app

import os
import StringIO
from PIL import Image, ImageDraw, ImageFont

def _pil_image(width, height, color_bgd, color_fgd, txt=None, font=None):
    """Image creation using Pillow (PIL fork)"""
    size = (width, height)
    hex_color_background = "#{0}".format(color_bgd)
    hex_color_foreground = "#{0}".format(color_fgd)
    im = Image.new("RGB", size, hex_color_background)
    # Draw on the image
    draw = ImageDraw.Draw(im)

    font_size = _calculate_font_size(width, height)
    font = _choose_font(font_size, font)

    w, h = font.getsize(txt)
    text_coord = ((width - w) / 2, (height - h) / 2)
    draw.text(text_coord, txt, fill=hex_color_foreground, font=font)

    del draw
    return im

def _serve_pil_image(im):
    """Serve the image created directly on the fly"""
    img_io = StringIO.StringIO()
    im.save(img_io, 'PNG')
    img_io.seek(0)
    return HttpResponse(img_io, mimetype='image/png')

def _calculate_font_size(width, height):
    min_side = min(width, height)
    return int(min_side / 4)


def _choose_font(font_size, font=None):
    """Choosing a font, the fallback is Yanone"""
    font_path = '{0}/font/{1}.otf'.format(os.path.dirname(get_app("fakeimg").__file__), font)
    print font_path
    try:
        return ImageFont.truetype(font_path, font_size)
    except IOError:
        # font not found: fallback
        return _choose_font(font_size, 'yanone')


def placeholder(request, width, height=None, bgd="cccccc", fgd="909090"):
    width = int(width)
    if not height:
        height = width
    height = int(height)
    txt = request.REQUEST.get('text', "{0} x {1}".format(width, height))
    font = request.REQUEST.get('font', 'yanone')
    retina = request.REQUEST.get('retina', None)
    if retina:
        width *= 2
        height *= 2
    im = _pil_image(width, height, bgd, fgd, txt, font)
    return _serve_pil_image(im)
