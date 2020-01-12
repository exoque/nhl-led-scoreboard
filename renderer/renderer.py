from abc import ABC, abstractmethod

from PIL import ImageFont, ImageDraw

from utils import center_text, right_text


class Renderer(ABC):

    def __init__(self):
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)
        self.text_color = (255, 255, 255)
        self.screen_width = 64
        self.screen_height = 32

    def render(self, image, frame_time):
        draw = ImageDraw.Draw(image)
        self._do_render(image, draw, frame_time)

    @abstractmethod
    def _do_render(self, image, draw, frame_time):
        pass

    def _render_center_text(self, draw, text, y, font=None):
        x = center_text(self.font_mini.getsize(str(text))[0], self._get_center())
        self._render_text(draw, text, x, y, font)

    def _render_left_text(self, draw, text, y, font=None):
        self._render_text(draw, text, 1, y, font)

    def _render_right_text(self, draw, text, y, font=None):
        x = right_text(self.font_mini.getsize(str(text))[0], self.screen_width)
        self._render_text(draw, text, x, y, font)

    def _render_text(self, draw, text, x, y, font=None):
        if font is None:
            font = self.font_mini

        draw.multiline_text((x, y), str(text), fill=self.text_color,
                            font=font,
                            align="center")

    def _get_center(self):
        return self.screen_width / 2
