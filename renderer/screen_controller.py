import time


class ScreenController:
    def __init__(self, config, render_surface, data_source):
        self.config = config
        self.render_surface = render_surface
        self.data_source = data_source
        self.renderers = []

    def main(self):
        self.update_data()
        self.draw()

    def update_data(self):
        pass

    def draw(self):
        for renderer in self.renderers:
            renderer.update_data(self.data)
            renderer.render(self.image, self.frame_time)

        time.sleep(0.05)


