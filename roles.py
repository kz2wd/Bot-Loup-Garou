import menu


class Role:
    def __init__(self, team, role_id, name, ability):
        self.team = team  # role's team, 1 for wolf, 2 for innocent, 3 for white wolf
        self.role_id = role_id  # role's id
        self.name = name  # role's name
        self.menu = menu.Menu([0], [0], 0, 1, -10)  # role's attributed menu
        self.ability = ability  # special variable for role's ability
        self.channel = []


def role_list():
    roles = [Role(2, 0, "Cupidon", 1), Role(2, 1, "Sorcière", 3), Role(2, 2, "Voyante", 0),
             Role(2, 3, "Chasseur", 0), Role(2, 4, "Dictateur", 1), Role(2, 5, "Fossoyeur", 0),
             Role(1, 6, "Loup Noir", 1), Role(3, 7, "Loup Blanc", 0), Role(1, 8, "Loup Garou", 0),
             Role(2, 9, "Villageois", 0)]

    # Cupidon : 1 = can put 2 players together, 0 = nothing
    # Sorcière : 3 = both potions, 2 = life potion, 1 = kill potion, 0 = no potion
    # Voyante : can see 1 player card per turn
    # Chasseur : at his death can shoot somebody
    # Dictateur : can try to take the power if he kill a wolf, else he die
    # Fossoyeur : at his death can indicate 2 players in opposite team
    # Loup Noir : 1 = can convert a player in team 2 to team 1, 0 = nothing
    # Loup blanc : have to win alone
    # Loup garou : eat human
    # Villageois : do nothing

    return roles
