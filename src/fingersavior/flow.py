import os
from functools import cache
from pathlib import Path
from random import randint
from typing import Generator, TYPE_CHECKING

from loguru import logger

from .command import Command, build_command, CommandTypes
from .handle_result import HandleResult
from .symbol import COMMAND_SYMBOL, ARG_SYMBOL, PROPERTY_SYMBOL
from .utils import random_int

if TYPE_CHECKING:
    from .game import Game


class Flow(object):
    chance = 100

    def __init__(self, name: str, file_path: str | Path, command: Command | None = None, extra_property: dict | None = None):
        self.name = name
        self.file_path = file_path
        self.command = command
        self.set_property(extra_property)

    def __repr__(self):
        return f"Flow(name={self.name}, command={self.command})"

    def set_property(self, data):
        if data:
            for name, value in data.items():
                if hasattr(self, name):
                    setattr(self, name, type(getattr(self, name))(value))
                else:
                    setattr(self, name, value)

    def handle(self, game: "Game", top_left: tuple[int, int], bottom_right: tuple[int, int]) -> HandleResult:
        if self.chance < 100 and randint(0, 100) > self.chance:
            return HandleResult.MISS
        if self.command:
            logger.debug(f"do {self.name} flow {self.command.name} command handler.")
            return self.command.handle(self, game, top_left, bottom_right)
        logger.debug(f"do {self.name} flow handler.")
        pos = random_int(top_left[0], bottom_right[0]), random_int(top_left[1], bottom_right[1])
        game.window.click(*pos)
        return HandleResult.BREAK


@cache
def parse_flow(file_path: str | Path) -> Flow:
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    file_name, _ = os.path.splitext(file_path.name)
    extra_property = None
    if PROPERTY_SYMBOL in file_name:
        extra_property = {}
        file_name, property_line = file_name[:file_name.find(PROPERTY_SYMBOL)], file_name[file_name.find(PROPERTY_SYMBOL) + 1:]
        for line in property_line.split(","):
            name, value = line.split("=")
            extra_property[name] = value
    if COMMAND_SYMBOL in file_name:
        file_name, command_line = file_name[:file_name.find(COMMAND_SYMBOL)], file_name[file_name.find(COMMAND_SYMBOL) + 1:]
        return Flow(file_name, file_path, build_command(command_line.split(ARG_SYMBOL)[0], *command_line.split(ARG_SYMBOL)[1:]), extra_property=extra_property)
    else:
        image_type = file_name.count(ARG_SYMBOL)
        if image_type >= 2:
            if image_type < 4:
                file_name, dx, dy, *_ = file_name.split(ARG_SYMBOL)
                return Flow(file_name, file_path, build_command(CommandTypes.OFFSET, int(dx), int(dy)), extra_property=extra_property)
            else:
                file_name, x1, y1, x2, y2, *_ = file_name.split(ARG_SYMBOL)
                return Flow(file_name, file_path, build_command(CommandTypes.REDIRECT, int(x1), int(y1), int(x2), int(y2)), extra_property=extra_property)
        else:
            return Flow(file_name, file_path, extra_property=extra_property)


def get_flows(source_dir: str | Path) -> "Generator[Flow]":
    if not isinstance(source_dir, Path):
        source_dir = Path(source_dir)
    if source_dir.exists() and source_dir.is_dir():
        for file_path in source_dir.iterdir():
            if file_path.is_file() and file_path.suffix == '.png':
                yield parse_flow(file_path)
