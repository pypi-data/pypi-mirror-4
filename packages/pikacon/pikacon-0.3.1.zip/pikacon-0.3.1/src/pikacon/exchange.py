class Exchange(object):
    """Exchange object."""

    def __init__(self, name, exchange_type="direct", durable=False,
                 auto_delete=False):
        self.name = name
        self.type = exchange_type
        self.durable = durable
        self.auto_delete = auto_delete
        self.queues = []

    def add_queue(self, queue):
        self.queues.append(queue)

    @property
    def queues(self):
        for queue in self.queues:
            yield queue
