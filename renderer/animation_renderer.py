from PIL import Image, ImageFont, ImageDraw, ImageSequence
import time
import logging


class AnimationRenderer:
    def __init__(self, render_surface):
        self.render_surface = render_surface

    def render(self, image_path):
        image = Image.open(image_path)
        frame_duration = image.info['duration'] / float(1000)

        for frame in ImageSequence.Iterator(image):
            logging.info("rendering frame, frame time {}, duration {}.".format(image.info['duration'], frame_duration))
            self.render_surface.render(frame.convert("RGB"))
            time.sleep(frame_duration)
        image.close()
