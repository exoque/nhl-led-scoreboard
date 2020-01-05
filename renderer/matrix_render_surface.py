from rgbmatrix import graphics


class MatrixRenderSurface:
    def __init__(self, matrix):
        self.matrix = matrix
        self.canvas = matrix.CreateFrameCanvas()

    def render(self, image):
        self.canvas.SetImage(image, 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
