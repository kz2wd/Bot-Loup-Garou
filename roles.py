from enum import Enum, auto


class Team(Enum):
    NOBODY = ("Dans le plus total des chaos tout le monde est mort") # used if for example everybody die / lose / leave ?
    WEREWOLF = ("Les loudivers remportent la partie!")
    VILLAGER = ("Les zumains assouvissent leur dominance sur Cludivers!")

    def __init__(self, victory_message):
        self._victory_message = victory_message

    @property
    def victory_message(self):
        return self._victory_message


class Role(Enum):
    WEREWOLF = ("Loudivers", Team.WEREWOLF)
    VILLAGER = ("Zumain", Team.VILLAGER)

    def __init__(self, name, team):
        self._name = name
        self._team = team

    @property
    def name(self):
        return self._name

    @property
    def team(self):
        return self._team



