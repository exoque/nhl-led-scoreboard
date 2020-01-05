class ImageRenderSurface:
    def __init__(self, path):
        self.path = path

    def render(self, image):
        image.save(self.path, "PNG")
