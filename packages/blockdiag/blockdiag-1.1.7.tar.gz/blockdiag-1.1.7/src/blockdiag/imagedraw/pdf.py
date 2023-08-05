# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
import sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from blockdiag.utils import urlutil, Box
from blockdiag.utils.fontmap import parse_fontpath
from blockdiag.utils.PDFTextFolder import PDFTextFolder as TextFolder


class PDFImageDraw(object):
    self_generative_methods = []

    def __init__(self, filename, size, **kwargs):
        self.canvas = canvas.Canvas(filename, pagesize=size)
        self.size = size
        self.fonts = {}

    def set_font(self, font):
        if font.path is None:
            msg = "Could not detect fonts, use --font opiton\n"
            raise RuntimeError(msg)

        if font.path not in self.fonts:
            path, index = parse_fontpath(font.path)
            if index:
                ttfont = TTFont(font.path, path, subfontIndex=index)
            else:
                ttfont = TTFont(font.path, path)
            pdfmetrics.registerFont(ttfont)

            self.fonts[font.path] = ttfont

        self.canvas.setFont(font.path, font.size)

    def set_render_params(self, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'), kwargs.get('thick'))

        params = {}
        if kwargs.get('fill', 'none') == 'none':
            params['fill'] = 0
        else:
            params['fill'] = 1

        if kwargs.get('outline') is None:
            params['stroke'] = 0
        else:
            params['stroke'] = 1

        return params

    def set_style(self, style, thick):
        if thick is None:
            thick = 1

        if style == 'dotted':
            self.canvas.setDash([2 * thick, 2 * thick])
        elif style == 'dashed':
            self.canvas.setDash([4 * thick, 4 * thick])
        elif style == 'none':
            self.canvas.setDash([0, 65535 * thick])
        elif re.search('^\d+(,\d+)*$', style or ""):
            self.canvas.setDash([int(n) * thick for n in style.split(',')])
        else:
            self.canvas.setDash()

    def set_stroke_color(self, color="black"):
        if isinstance(color, basestring):
            self.canvas.setStrokeColor(color)
        elif color:
            rgb = (color[0] / 256.0, color[1] / 256.0, color[2] / 256.0)
            self.canvas.setStrokeColorRGB(*rgb)
        else:
            self.set_stroke_color()

    def set_fill_color(self, color="white"):
        if isinstance(color, basestring):
            if color != 'none':
                self.canvas.setFillColor(color)
        elif color:
            rgb = (color[0] / 256.0, color[1] / 256.0, color[2] / 256.0)
            self.canvas.setFillColorRGB(*rgb)
        else:
            self.set_fill_color()

    def path(self, pd, **kwargs):
        params = self.set_render_params(**kwargs)
        self.canvas.drawPath(pd, **params)

    def rectangle(self, box, **kwargs):
        x = box[0]
        y = self.size[1] - box[3]
        width = box[2] - box[0]
        height = box[3] - box[1]

        if 'thick' in kwargs and kwargs['thick'] is not None:
            self.canvas.setLineWidth(kwargs['thick'])

        params = self.set_render_params(**kwargs)
        self.canvas.rect(x, y, width, height, **params)

        if 'thick' in kwargs:
            self.canvas.setLineWidth(1)

    def text(self, xy, string, font, **kwargs):
        self.set_font(font)
        self.set_fill_color(kwargs.get('fill'))
        self.canvas.drawString(xy[0], self.size[1] - xy[1], string)

    def textarea(self, box, string, font, **kwargs):
        self.canvas.saveState()

        if 'rotate' in kwargs and kwargs['rotate'] != 0:
            angle = 360 - int(kwargs['rotate']) % 360
            self.canvas.rotate(angle)

            if angle == 90:
                box = Box(-box.y2, box.x1, -box.y1, box.x1 + box.width)
                box = box.shift(x=self.size.y, y=self.size.y)
            elif angle == 180:
                box = Box(-box.x2, -box.y2, -box.x1, -box.y2 + box.height)
                box = box.shift(y=self.size.y * 2)
            elif angle == 270:
                box = Box(box.y1, -box.x2, box.y2, -box.x1)
                box = box.shift(x=-self.size.y, y=self.size.y)

        self.set_font(font)
        lines = TextFolder(box, string, font, adjustBaseline=True,
                           canvas=self.canvas, **kwargs)

        if kwargs.get('outline'):
            outline = kwargs.get('outline')
            self.rectangle(lines.outlinebox, fill='white', outline=outline)

        rendered = False
        for string, xy in lines.lines:
            self.text(xy, string, font, **kwargs)
            rendered = True
        self.canvas.restoreState()

        if not rendered and font.size > 0:
            font.size = int(font.size * 0.8)
            self.textarea(box, string, font, **kwargs)

    def line(self, xy, **kwargs):
        self.set_stroke_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'), kwargs.get('thick'))

        if 'thick' in kwargs and kwargs['thick'] is not None:
            self.canvas.setLineWidth(kwargs['thick'])

        p1 = xy[0]
        y = self.size[1]
        for p2 in xy[1:]:
            self.canvas.line(p1.x, y - p1.y, p2.x, y - p2.y)
            p1 = p2

        if 'thick' in kwargs:
            self.canvas.setLineWidth(1)

    def arc(self, xy, start, end, **kwargs):
        start, end = 360 - end, 360 - start
        r = (360 + end - start) % 360

        self.set_render_params(**kwargs)
        y = self.size[1]
        self.canvas.arc(xy[0], y - xy[3], xy[2], y - xy[1], start, r)

    def ellipse(self, xy, **kwargs):
        params = self.set_render_params(**kwargs)
        y = self.size[1]
        self.canvas.ellipse(xy[0], y - xy[3], xy[2], y - xy[1], **params)

    def polygon(self, xy, **kwargs):
        pd = self.canvas.beginPath()
        y = self.size[1]
        pd.moveTo(xy[0][0], y - xy[0][1])
        for p in xy[1:]:
            pd.lineTo(p[0], y - p[1])

        params = self.set_render_params(**kwargs)
        self.canvas.drawPath(pd, **params)

    def loadImage(self, filename, box):
        x = box[0]
        y = self.size[1] - box[3]
        w = box[2] - box[0]
        h = box[3] - box[1]

        if urlutil.isurl(filename):
            from reportlab.lib.utils import ImageReader
            try:
                filename = ImageReader(filename)
            except:
                msg = "WARNING: Could not retrieve: %s\n" % filename
                sys.stderr.write(msg)
                return
        self.canvas.drawImage(filename, x, y, w, h, mask='auto',
                                  preserveAspectRatio=True)

    def save(self, filename, size, format):
        # Ignore size and format parameter; compatibility for ImageDrawEx.

        self.canvas.showPage()
        self.canvas.save()
