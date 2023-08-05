import os

class Common(object):
    def __init__(self):
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./static/")
