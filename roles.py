import menu


class Role:
    def __init__(self, team, role_id, name):
        self.team = team
        self.role_id = role_id
        self.name = name
        self.menu = menu.Menu([i for i in range(3)], [250717160521859072], [0], 4, 10)
