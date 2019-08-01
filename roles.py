import menu
import random


class Role:
    def __init__(self, team, role_id, name):
        self.team = team  # role's team, 1 for wolf, 2 for innocent
        self.role_id = role_id  # role's id
        self.name = name  # role's name
        self.menu = menu.Menu([i for i in range(3)], [0], [0], 1, 10)  # role's attributed menu
        self.ability = 0  # special variable for role's ability


def repartitor(player_list, result_list):
    print(result_list)
    del result_list[0][0]
    random.shuffle(result_list)
    for i, item in enumerate(player_list):
        item.role = result_list[i]
    return player_list

