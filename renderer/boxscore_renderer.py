import time

from PIL import ImageDraw, Image

from renderer.renderer import Renderer
import debug


class BoxscoreRenderer(Renderer):
    def __init__(self, data, screen_config, render_surface):
        super().__init__()
        self.screen_config = screen_config
        debug.log(data)
        self.data = data
        self.render_surface = render_surface
        self.display_time = 3
        self.start_time = None
        self.current_item = 0

    def _do_render(self, image, draw, frame_time):
        #self._render_left_text(draw, "Left text", 1)
        #self._render_center_text(draw, "Center text", 10)
        #self._render_right_text(draw, "Right text", 19)

        debug.log(self.current_item)

        goal_data = self.__get_goal_to_display(self.data)
        self._render_left_text(draw, "{} {} {}".format(goal_data.time, goal_data.team, goal_data.strength), 0)
        self._render_right_text(draw, "{}-{}".format(goal_data.result.away, goal_data.result.home), 0)
        self._render_left_text(draw, self.__get_last_name(goal_data.scorer), 8)
        self._render_left_text(draw, self.__get_last_name(goal_data.assist1), 16)
        self._render_left_text(draw, self.__get_last_name(goal_data.assist2), 24)

        self.render_surface.render(image)

        # Refresh the Data image.
        image = Image.new('RGB', (self.screen_width, self.screen_height))
        draw = ImageDraw.Draw(image)

    def __get_goal_to_display(self, data):
        if self.start_time is not None:
            debug.log(time.time() - self.start_time)
            if self.display_time <= time.time() - self.start_time:
                self.current_item = (self.current_item + 1) % len(self.data)
                self.start_time = time.time()
        else:
            self.start_time = time.time()

        return data[self.current_item]

    @staticmethod
    def __get_last_name(name):
        return name.split()[1]
