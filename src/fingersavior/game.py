import win32ui
from loguru import logger

from .flow import Flow, get_flows
from .handle_result import HandleResult
from .utils import load_image, random_sleep
from .window import Window


class Game(object):
    def __init__(self, hwnd):
        self.window = Window(hwnd=hwnd)
        self.last_flow: Flow | None = None
        self.next_flow_name: str | None = None

    def do_flow(self, flows: list[Flow]):
        self.window.frame_shot()
        self.last_flow = None
        for flow in flows:
            if self.next_flow_name and flow.name != self.next_flow_name:
                continue
            if self.last_flow and flow.name == self.last_flow.name:
                # Each time through the flow loop, the same name is executed only once
                continue
            img_obj = load_image(flow.file_path)
            if img_obj is None:
                logger.debug(f"{flow.file_path} file not found")
                continue
            result = self.window.find(img_obj)
            if result:
                logger.debug(f"flow {flow.name} found!")
                top_left_corner, buttom_right_corner = result['rectangle'][0], result['rectangle'][3]
                flowresult = flow.handle(self, top_left_corner, buttom_right_corner)
                self.last_flow = flow
                if flowresult == HandleResult.BREAK:
                    logger.debug("跳出循环")
                    break
                elif flowresult == HandleResult.CONTINUE:
                    logger.debug("跳过循环")
                    continue
                elif flowresult == HandleResult.RETURN:
                    logger.debug("结束本次flow循环")
                    return
                elif flowresult == HandleResult.EXIT:
                    logger.debug("结束进程")
                    exit(0)
                else:
                    pass
        else:
            self.next_flow_name = None
            logger.debug("本轮没有找到任何流程")
        random_sleep()

    def run(self, source_dir):
        self.window.resize()
        logger.info('start run: {}'.format(source_dir))
        while True:
            flows = sorted(get_flows(source_dir), key=lambda d: d.name)
            try:
                self.do_flow(flows)
            except win32ui.error:
                pass
