import operator
import threading

from player import Player


class VoteCollector:
    def __init__(self, options, voters: list[Player]):
        self.options = {opt: 0 for opt in options}
        self.mutex = threading.Lock()
        self.allowed_voters = voters
        self.has_voted: set[Player] = set()
        self.expected_votes = len(voters)

    # CONSIDER THAT VOTER is included in the voters list!
    # Returns True if all voters have voted
    async def add_vote(self, option, voter: Player) -> bool:
        with self.mutex:
            try:
                self.options[option] += 1
                self.expected_votes -= 0 if voter in self.has_voted else 1
                self.has_voted.add(voter)
            except KeyError as ignored:
                pass
        return self.expected_votes == 0

    def get_single_most(self) -> tuple[any, int] | None:
        max_votes = max((v for k, v in self.options.items()))
        most_voted = [(choice, amount) for (choice, amount) in self.options.items() if amount == max_votes]
        if len(most_voted) == 1:
            return most_voted[0]
        return None
