# Here you can find all about menus
import msg
import reactions


class Menu:
    def __init__(self, choice, allowed_id, channel, number_of_response, active_state):
        self.choice = choice  # list of all choice
        self.allowed_id = allowed_id  # list of all player(s)'s id allowed to answer
        self.channel = channel
        self.reaction_allowed = True
        self.message_allowed = True
        self.number_of_response = number_of_response
        self.result_list = []
        for i in range(len(self.allowed_id)):
            self.result_list.append([i])
            for j in range(self.number_of_response):
                self.result_list[i].append(-1)
        self.active_state = active_state

    async def display(self):
        x = await self.channel.send((
            "\n".join("`{} : {}`".format(msg.alphabet[i], item) for i, item in enumerate(self.choice))) +
                                "\n```Faites votre choix```")

        if self.reaction_allowed:
            for i in range(len(self.choice)):
                await x.add_reaction(reactions.menu[i])




