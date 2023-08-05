class Queue(object):
    """Pikacon queue object."""

    def __init__(self, name, durable=True, exclusive=True, **args):
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.args = args
