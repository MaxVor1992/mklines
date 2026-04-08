import threading
import request_parser


class ParseThread(threading.Thread):
    def __init__(self, search, engine, region, depth, callback=None):
        self.progress = 0
        super().__init__()
        self.search = search
        self.engine = engine
        self.region = region
        self.depth = depth
        self.callBack = callback

    def run(self, ):
        res = ParseThread.launch_parser(self.search, self.engine, self.region, self.depth)
        if self.callBack:
            self.callBack(res)

    @staticmethod
    def launch_parser(search, engine, region, depth):
        system = "yandex" if engine == 1 else "google"
        parser = request_parser.SearchParser(search, system, count=depth, repeats=1, output_file=None,
                                             region=region)
        return parser.run_parse()
