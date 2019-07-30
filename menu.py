# Here you can find all about menus
import msg
import reactions


class Menu:
    def __init__(self, choice, allowed_id, channel):
        self.choice = choice  # list of all choice
        self.allowed_id = allowed_id  # list of all player(s)'s id allowed to answer
        self.channel = channel
        self.reaction_allowed = True
        self.message_allowed = True
        self.number_of_response = 1

    async def display(self):
        x = await self.channel.send((
            "\n".join("{} : {}".format(msg.alphabet[i], item) for i, item in enumerate(self.choice))) +
                                "\n```Faites votre choix```")

        if self.reaction_allowed:
            for i in range(len(self.choice)):
                await x.add_reaction(reactions.menu[i])

    def get_response(self):
        result_list = []
        if self.reaction_allowed:
            async def on_reaction_add(reaction, user):
                for i in self.allowed_id:
                    if user.id == i:
                        for j in reactions.menu:
                            if j == reaction:
                                result_list = []

        if self.message_allowed:
            async def on_message(message):
                for i in self.allowed_id:
                    if message.author.id == i:
                        print("yes message menu")


