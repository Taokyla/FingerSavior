import time
from enum import StrEnum
from random import choice, randint
from typing import TYPE_CHECKING

from loguru import logger

from .handle_result import HandleResult
from .utils import random_int

if TYPE_CHECKING:
    from .flow import Flow
    from .game import Game

command_factory = {}


class CommandTypes(StrEnum):
    OFFSET = "offset"  # 偏移点击
    REDIRECT = "redirect"  # 重定向点击范围
    GOTO = "goto"  # 指定下一次执行的名称，跳出
    SAVE = "save"  # 截屏并跳过，继续flow循环
    EXIT = "exit"  # 退出
    SKIP = "skip"  # 跳过
    RANDOMY = "randomy"  # 一个很难用到的东西
    RANDOMX = "randomx"  # 一个很难用到的东西
    DELAY = "delay"  # 额外延迟
    JUMP = "jump"  # 跳到指定位置，只能是当前flow比他后面的命令
    COUNT = "count"  # 累计次数退出
    USELASTCLICK = "uselastclick"  # 使用上一个flow的点击位置


class Command(object):

    def __init__(self, command: str):
        self.name = command

    def __repr__(self):
        return f"Command({self.name})"

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        pos = random_int(top_left[0], bottom_right[0]), random_int(top_left[1], bottom_right[1])
        game.window.click(*pos)
        return HandleResult.BREAK


class CommandUseLastClick(Command):

    def __init__(self, command: str):
        super().__init__(command)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        if game.window.last_click:
            logger.debug(f"使用上次相同点击位置,{game.window.last_click}")
            game.window.click(*game.window.last_click)
            return HandleResult.BREAK
        return HandleResult.CONTINUE


class CommandCount(Command):
    counting: dict[int, dict[str, int]] = {}

    def __init__(self, command: str, count: int | str):
        super().__init__(command)
        self.count = int(count)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        result = super().handle(flow, game, top_left, bottom_right)
        game_counts = CommandCount.counting.get(game.window.hwnd)
        if game_counts:
            last_count = game_counts.get(flow.name, 0)
        else:
            CommandCount.counting[game.window.hwnd] = {flow.name: 0}
            last_count = 0
        count = last_count + 1
        logger.info(f"{game.window.hwnd}:{flow.name} count {count}/{self.count}")
        CommandCount.counting[game.window.hwnd][flow.name] = count
        if count >= int(self.count):
            return HandleResult.EXIT
        return result


class CommandOffset(Command):
    def __init__(self, command: str, x: int | str, y: int | str):
        super().__init__(command)
        self.dx = int(x)
        self.dy = int(y)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        top_left = top_left[0] + self.dx, top_left[1] + self.dy
        bottom_right = bottom_right[0] + self.dx, bottom_right[1] + self.dy
        return super().handle(flow, game, top_left, bottom_right)


class CommandRedirect(Command):
    def __init__(self, command: str, left_x: int | str, left_y: int | str, right_x: int | str, right_y: int | str):
        super().__init__(command)
        self.top_left = int(left_x), int(left_y)
        self.bottom_right = int(right_x), int(right_y)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        return super().handle(flow, game, self.top_left, self.bottom_right)


class CommandSave(Command):
    def __init__(self, command: str):
        super().__init__(command)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        game.window.take_screen_shot()
        return HandleResult.CONTINUE


class CommandGoto(Command):
    def __init__(self, command: str, next_flow_name: str):
        super().__init__(command)
        self.next = next_flow_name

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        game.next_flow_name = self.next
        return HandleResult.RETURN


class CommandJump(Command):
    def __init__(self, command: str, next_flow_name: str):
        super().__init__(command)
        self.next = next_flow_name

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        game.next_flow_name = self.next
        return HandleResult.CONTINUE


class CommandExit(Command):
    def __init__(self, command: str):
        super().__init__(command)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        return HandleResult.EXIT


class CommandSkip(Command):
    def __init__(self, command: str):
        super().__init__(command)

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        return HandleResult.CONTINUE


class CommandRandomY(Command):
    def __init__(self, command: str, dx, *offset_y):
        super().__init__(command)
        self.dx = int(dx)
        self.offset_y = [int(y) for y in offset_y]

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        offset_y = choice(self.offset_y)
        top_left = top_left[0] + self.dx, top_left[1] + offset_y
        bottom_right = bottom_right[0] + self.dx, bottom_right[1] + offset_y
        return super().handle(flow, game, top_left, bottom_right)


class CommandRandomX(Command):
    def __init__(self, command: str, dy, *offset_x):
        super().__init__(command)
        self.dy = int(dy)
        self.offset_x = [int(x) for x in offset_x]

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        offset_x = choice(self.offset_x)
        top_left = top_left[0] + offset_x, top_left[1] + self.dy
        bottom_right = bottom_right[0] + offset_x, bottom_right[1] + self.dy
        return super().handle(flow, game, top_left, bottom_right)


class CommandDelay(Command):
    def __init__(self, command: str, *delaytime):
        super().__init__(command)
        if len(delaytime) == 0:
            self.delay = 1
        elif len(delaytime) == 1:
            self.delay = int(delaytime)
        else:
            self.delay = int(delaytime[0]), int(delaytime[1])

    def handle(self, flow: "Flow", game: "Game", top_left, bottom_right):
        if isinstance(self.delay, tuple):
            delay = randint(*self.delay)
        else:
            delay = self.delay
        result = super().handle(flow, game, top_left, bottom_right)
        time.sleep(delay)
        return result


command_factory[CommandTypes.OFFSET] = CommandOffset
command_factory[CommandTypes.SAVE] = CommandSave
command_factory[CommandTypes.REDIRECT] = CommandRedirect
command_factory[CommandTypes.EXIT] = CommandExit
command_factory[CommandTypes.SKIP] = CommandSkip
command_factory[CommandTypes.RANDOMY] = CommandRandomY
command_factory[CommandTypes.RANDOMX] = CommandRandomX
command_factory[CommandTypes.DELAY] = CommandDelay
command_factory[CommandTypes.JUMP] = CommandJump
command_factory[CommandTypes.COUNT] = CommandCount
command_factory[CommandTypes.USELASTCLICK] = CommandUseLastClick


def build_command(command: str | CommandTypes, *args, **kwargs) -> Command:
    if command in command_factory:
        return command_factory[command](command, *args, **kwargs)
    return Command(command)
