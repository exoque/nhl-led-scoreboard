from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import logging


class MatrixRenderSurface:
    def __init__(self, matrix_options):
        self.matrix = RGBMatrix(options=matrix_options)
        self.canvas = self.matrix.CreateFrameCanvas()
        logging.info("({}x{})".format(self.matrix.width, self.matrix.height))

    def render(self, image):
        self.canvas.SetImage(image, 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
