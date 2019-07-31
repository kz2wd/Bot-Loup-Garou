import menu


class Role:
    def __init__(self, team, role_id, name):
        self.team = team
        self.role_id = role_id
        self.name = name
        self.menu = menu.Menu([i for i in range(3)], [0], [0], 1, 10)
