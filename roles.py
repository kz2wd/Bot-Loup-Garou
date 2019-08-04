import menu


class Role:
    def __init__(self, team, role_id, name, ability):
        self.team = team  # role's team, 1 for wolf, 2 for innocent, 3 for white wolf
        self.role_id = role_id  # role's id
        self.name = name  # role's name
        self.menu = menu.Menu([i for i in range(3)], [0], [0], 1, 10)  # role's attributed menu
        self.ability = ability  # special variable for role's ability


def role_list():
    role_list = []
    role_list.append(Role(2, 0, "Cupidon", 1))  # 1 = can put 2 players together, 0 = nothing
    role_list.append(Role(2, 1, "Sorcière", 3))  # 3 = both potions, 2 = life potion, 1 = kill potion, 0 = no potion
    role_list.append(Role(2, 2, "Voyante", 0))  # can see 1 player card per turn
    role_list.append(Role(2, 3, "Chasseur", 0))  # can shoot somebody on death
    role_list.append(Role(2, 4, "Dictateur", 1))  # can try to take the power if he kill a wolf, else he die
    role_list.append(Role(2, 5, "Fossoyeur", 0))  # can indicate 2 players in opposite team
    role_list.append(Role(1, 6, "Loup Noir", 1))  # 1 = can convert a player in team 2 to team 1, 0 = nothing
    role_list.append(Role(3, 7, "Loup Blanc", 0))  # have to win alone
    role_list.append(Role(1, 8, "Loup Garou", 0))  # eat human
    role_list.append(Role(2, 9, "Villageois", 0))  # do nothing
    return role_list

