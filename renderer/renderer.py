from abc import ABC, abstractmethod
from math import floor

from PIL import ImageFont, ImageDraw, Image

from utils import center_text, right_text


class Renderer(ABC):

    def __init__(self, config, render_surface):
        self.config = config
        self.font = ImageFont.truetype("fonts/score_large.otf", floor(self.config.screen_config.height / 2))
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", floor(self.config.screen_config.height / 4))
        self.text_color = (255, 255, 255)
        self.render_surface = render_surface
        self.text_y_pos_init = 0
        self.text_y_pos = 0
        self.data = None

    def render(self, image, frame_time):
        self.text_y_pos = self.text_y_pos_init
        draw = ImageDraw.Draw(image)
        self._do_render(image, draw, frame_time)

    def update_data(self, data):
        self.data = data

    @abstractmethod
    def _do_render(self, image, draw, frame_time):
        pass

    def _refresh_screen(self, image):
        self.render_surface.render(image)

        # Refresh the Data image.
        image = Image.new('RGB', (self._get_screen_width(), self._get_screen_height()))

    def _render_center_text(self, draw, text, y, font=None):
        x = center_text(self._get_text_length(font, text), self._get_center())
        self._render_text(draw, text, x, y, font)

    def _render_left_text(self, draw, text, y, font=None):
        self._render_text(draw, text, 1, y, font)

    def _render_right_text(self, draw, text, y, font=None):
        x = right_text(self._get_text_length(font, text), self._get_screen_width())
        self._render_text(draw, text, x, y, font)

    def _render_text(self, draw, text, x, y, font=None):
        draw.multiline_text((x, y), str(text), fill=self.text_color,
                            font=self.__get_font(font),
                            align="center")

    def _get_text_length(self, font, text):
        return self.__get_font(font).getsize(str(text))[0]

    def _get_center(self):
        return self._get_screen_width() / 2

    def __get_font(self, font):
        return self.font_mini if font is None else font

    def _get_screen_width(self):
        return self.config.screen_config.width

    def _get_screen_height(self):
        return self.config.screen_config.height

    def _move_to_next_line(self):
        self.text_y_pos = self.text_y_pos + (self._get_screen_height() / 4)
        return self.text_y_pos

    def _get_line_height(self):
        return self._get_screen_height() / 4
