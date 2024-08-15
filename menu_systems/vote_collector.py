import operator
import threading

from player import Player


class VoteCollector:
    def __init__(self, options, voters: list[Player]):
        self.options = {opt: 0 for opt in options}
        self.mutex = threading.Lock()
        self.allowed_voters = voters
        self.has_voted: dict[Player, any] = dict()
        self.expected_votes = len(voters)

    # CONSIDER THAT VOTER is included in the voters list!
    # Returns True if all voters have voted
    async def add_vote(self, option, voter: Player) -> bool:
        with self.mutex:
            self.options[option] += 1
            if voter in self.has_voted:
                self.options[self.has_voted[voter]] -= 1  # remove previous vote
            self.has_voted[voter] = option  # update new vote

        return len(self.has_voted) == self.expected_votes

    def get_single_most(self) -> tuple[any, int] | None:
        max_votes = max((v for k, v in self.options.items()))
        if max_votes == 0: return None
        most_voted = [(choice, amount) for (choice, amount) in self.options.items() if amount == max_votes]
        if len(most_voted) == 1:
            return most_voted[0]
        return None
