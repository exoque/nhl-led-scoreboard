from PIL import Image, ImageFont, ImageDraw, ImageSequence
import time
import debug


class AnimationRenderer:
    def __init__(self, render_surface, image_path):
        self.render_surface = render_surface
        self.image = Image.open(image_path)
        self.frameNo = 0

    def render(self):
        frame_duration = self.image.info['duration'] / float(1000)

        for frame in ImageSequence.Iterator(self.image):
            debug.info("rendering frame, frame time {}, duration {}.".format(self.image.info['duration'], frame_duration))
            self.render_surface.render(frame.convert("RGB"))
            time.sleep(frame_duration)
        self.image.close()
