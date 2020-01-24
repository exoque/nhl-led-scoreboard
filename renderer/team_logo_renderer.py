from PIL import Image, ImageFont, ImageDraw


class TeamLogoRenderer:
    def __init__(self, data, screen_config):
        self.screen_config = screen_config
        self.data = data

    def draw_team_logo(self, image, team_type, team_id):
        team_logo_pos = self.screen_config.team_logos_pos[str(team_id)][team_type]
        team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[team_id]['abbreviation']))
        image.paste(team_logo.convert("RGB"), (team_logo_pos["x"], team_logo_pos["y"]))
        team_logo.close()

    def draw_team_logos(self, image, home_team_id, away_team_id):
        self.draw_team_logo(image, 'home', home_team_id)
        self.draw_team_logo(image, 'away', away_team_id)
