import tkinter as tk
from PIL import ImageTk


class TkInterRenderSurface:
    def __init__(self, root):
        self.panel = tk.Label(root)

    def render(self, image):
        img = ImageTk.PhotoImage(image.resize((512, 256)))
        self.panel.config(image=img)
        self.panel.image = img
        self.panel.pack(side="bottom", fill="both", expand="yes")
