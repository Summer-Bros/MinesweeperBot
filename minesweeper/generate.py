import random
from typing import AsyncGenerator, Dict, Generator
import nextcord
import numpy
from nextcord.ext import commands

from minesweeper import TESTING_GUILD_IDS


class Array:
    lookup: Dict[int, str] = {
        -1: "boom",
        0: "zero",
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
    }

    def __init__(self, size: tuple[int, int], seed: int, mines: int) -> None:
        self.field = numpy.zeros(size, dtype=int)
        self.seed = seed
        self.mines = min(mines, size[0] * size[1])
        self.set_mines()
        self.set_points()

    def set_mines(self) -> None:
        generator = random.Random()
        generator.seed(self.seed)
        truths = (
            bin(
                generator.randint(
                    0, 2 ** (exponent := self.field.shape[0] * self.field.shape[1]) - 1
                )
            )
            .replace("0b", "")
            .zfill(exponent)
        )
        for bit, coords in zip(map(int, truths), generator.sample(tuple(self.iter_coords()), exponent)):
            if bit and numpy.sum(self.field) + self.mines > 0:
                self.field[coords] = -1

    def iter_coords(self) -> Generator[tuple[int, int], None, None]:
        for x_co in range(self.field.shape[0]):
            for y_co in range(self.field.shape[1]):
                yield (x_co, y_co)

    def mine_choices(self) -> Generator[tuple[int, int], None, None]:
        for x_co, y_co in self.iter_coords():
            if self.field[x_co, y_co] >= 0:
                yield (x_co, y_co)

    def set_points(self) -> None:
        for x_co, y_co in self.mine_choices():
            if self.field[x_co, y_co] >= 0:
                for point in self.neighbor_points(x_co, y_co):
                    if self.field[point] == -1:
                        self.field[x_co, y_co] += 1

    def neighbor_points(
        self, x_co: int, y_co: int
    ) -> Generator[tuple[int, int], None, None]:
        choices = (
            (x_co + 1, y_co),
            (x_co - 1, y_co),
            (x_co + 1, y_co + 1),
            (x_co - 1, y_co + 1),
            (x_co + 1, y_co - 1),
            (x_co - 1, y_co - 1),
            (x_co, y_co + 1),
            (x_co, y_co - 1),
        )
        for choice_x, choice_y in choices:
            if (
                self.field.shape[0] > choice_x >= 0
                and self.field.shape[1] > choice_y >= 0
            ):
                yield (choice_x, choice_y)

    def export(self, hidden: bool) -> Generator[str, None, None]:
        style = "||" if hidden else ""
        for y_co in range(self.field.shape[1]):
            for x_co in range(self.field.shape[0]):
                yield f"{style}:{self.lookup.get(self.field[x_co, y_co])}:{style}"
            yield "\n"


class Game(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @nextcord.slash_command(guild_ids=TESTING_GUILD_IDS)
    async def minesweeper(
        self,
        interaction: nextcord.Interaction,
        size: str = "9,9",
        mines: int = 20,
        hidden: bool = True,
    ) -> None:
        board = Array(tuple(map(int, size.split(","))), interaction.user.id, mines)
        await interaction.response.send_message("".join(board.export(hidden=hidden)))
