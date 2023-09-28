import ctypes
import sys
import time
from pathlib import Path

from loguru import logger
from pathos.multiprocessing import ProcessPool

from fingersavior.game import Game
from fingersavior.window import Window


def get_model(*excludes):
    work_directory = Path.cwd()
    for dir_path in work_directory.iterdir():
        if dir_path.name.startswith('.') or dir_path.name.startswith('_') or dir_path.is_file() or dir_path.name in excludes:
            continue
        yield dir_path


def run(hwnd, name):
    game = Game(hwnd)
    game.run(name)


if __name__ == '__main__':
    if not Window.is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        logger.remove()
        logger.add(sys.stdout, level='INFO')
        label = '阴阳师-网易游戏'
        models = [m for m in get_model("src", "lib", "config", "venv", "env")]
        if not models:
            logger.error("no model found!")
            exit(1)
        for index, model in enumerate(models):
            print(f'{index + 1}. {model.name}')
        select = int(input('selection:')) - 1
        name = models[select]
        wins = Window.get_all_windows(label)
        total = len(wins)
        if total > 1:
            try:
                pool = ProcessPool(nodes=total)
                names = [name] * len(wins)
                pool.imap(run, wins, names)
            except Exception as e:
                print(e)
                logger.error("Error: 无法启动线程")
            while True:
                time.sleep(5)
        elif total == 1:
            game = Game(wins[0])
            game.run(name)
        else:
            logger.error("no window find!")
