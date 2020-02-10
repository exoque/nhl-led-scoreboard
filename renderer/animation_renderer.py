from PIL import Image, ImageFont, ImageDraw, ImageSequence
import time
import logging

from renderer.renderer import Renderer


class AnimationRenderer(Renderer):
    KEY_ANIMATION_RENDERER = 'animation_renderer'

    def __init__(self, config, render_surface, image_path):
        super().__init__(config, render_surface)
        self.image_path = image_path

    def _do_render(self, image, draw, frame_time):
        animation = Image.open(self.image_path)
        frame_duration = animation.info['duration'] / float(1000)

        for frame in ImageSequence.Iterator(animation):
            logging.info("rendering frame, frame time {}, duration {}.".format(animation.info['duration'], frame_duration))
            self.render_surface.render(frame.convert("RGB"))
            time.sleep(frame_duration)
        animation.close()
