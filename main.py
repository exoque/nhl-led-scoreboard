import time
from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.data import Data
from renderer.matrix_render_surface import MatrixRenderSurface
from renderer.image_render_surface import ImageRenderSurface
import debug


from data.data_source_nhl import DataSourceNhl

SCRIPT_NAME = "NHL Scoreboard"
SCRIPT_VERSION = "0.1.0"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Print some basic info on startup
debug.info("{} - v{}".format(SCRIPT_NAME, SCRIPT_VERSION))

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", args)
debug.set_debug_status(config)

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

time_stamp = '20200118_183400'
while True:
    time_stamp, event_list = nhl_data_source.load_game_stats_update(2019020743, time_stamp)
    #time_stamp, event_list = nhl_data_source.load_game_stats_update(2019020755, time_stamp)
    time.sleep(10)



#data = Data(config)
#matrixRenderSurface = MatrixRenderSurface(matrixOptions)
#MainRenderer(matrixRenderSurface, data).render()

#imageRenderSurface = ImageRenderSurface('/home/ch/Pictures/nhl-scoreboard.png')
#MainRenderer(imageRenderSurface, data).render()
