import time


class ScreenController:
    def __init__(self, config, render_surface):
        self.config = config
        self.render_surface = render_surface
        self.renderers = []

    def draw(self):
        for renderer in self.renderers:
            renderer.update_data(self.data)
            renderer.render(self.image, self.frame_time)

        time.sleep(0.05)
