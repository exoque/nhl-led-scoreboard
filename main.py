import threading

from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from renderer.tkinter_render_surface import TkInterRenderSurface
from utils import args, led_matrix_options
from renderer.matrix_render_surface import MatrixRenderSurface
from renderer.image_render_surface import ImageRenderSurface
import logging

import tkinter as tk

from data.data_source_nhl import DataSourceNhl


class DataThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def run(self):
        try:
            MainRenderer(tKInterRenderSurface, config).render()
        except KeyboardInterrupt:
            exit()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


SCRIPT_NAME = "NHL Scoreboard"
SCRIPT_VERSION = "0.1.0"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

logging.basicConfig(filename='nhl-led-scoreboard.log', level=logging.INFO)

# Print some basic info on startup
logging.info("{} - v{}".format(SCRIPT_NAME, SCRIPT_VERSION))

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", args)


nhl_data_source = DataSourceNhl(config)
#print(nhl_data_source.load_teams())
#print(nhl_data_source.load_game_info(5))
#print(nhl_data_source.load_day_schedule("2020-01-10"))
#print(nhl_data_source.load_game_stats(2019020743))
#print(nhl_data_source.load_game_stats_update(2019020691, '20200111_065130'))
#print(nhl_data_source.load_game_stats_update(2019020691, '20200111_065030'))
#print(nhl_data_source.load_game_stats_update(2019020691, '20200111_064930'))
#print(nhl_data_source.load_game_stats_update(2019020691, '20200111_064830'))
#print(nhl_data_source.load_game_stats_update(2019020693, '20200112_023402'))

#print(nhl_data_source.load_game_stats_update(2019020693, '4'))

#time_stamp = '20200118_183400'
#while True:
#    time_stamp, event_list = nhl_data_source.load_game_stats_update(2019020743, time_stamp)
    #time_stamp, event_list = nhl_data_source.load_game_stats_update(2019020755, time_stamp)
#    time.sleep(10)


if config.debug_output:
    main = tk.Tk()
    main.title('NHL Scoreboard')  # sets window title
    main.geometry('512x256')  # sets default window size (pixels)
    tKInterRenderSurface = TkInterRenderSurface(main)
    data_thread = DataThread().start()
    main.mainloop()
    data_thread.stop()

    # Render to image, enable if tkinter not available
    #imageRenderSurface = ImageRenderSurface(config.image_output_file)
    #MainRenderer(imageRenderSurface, config).render()
else:
    matrixRenderSurface = MatrixRenderSurface(matrixOptions)
    MainRenderer(matrixRenderSurface, config).render()


