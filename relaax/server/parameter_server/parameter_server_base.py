class ParameterServerBase(object):
    def __init__(self, saver_factory, metrics_factory):
        self.initialize_algorithm()
        self.saver = saver_factory(self.make_checkpoint())
        self.metrics = metrics_factory(self.n_step)

    def close(self):
        raise NotImplementedError

    def restore_latest_checkpoint(self):
        checkpoint_ids = self.saver.checkpoint_ids()
        if len(checkpoint_ids) > 0:
            self.saver.restore_checkpoint(max(checkpoint_ids))

    def save_checkpoint(self):
        self.saver.save_checkpoint(self.n_step())

    def initialize_algorithm(self):
        raise NotImplementedError

    def make_checkpoint(self):
        raise NotImplementedError

    def get_session(self):
        raise NotImplementedError

    def n_step(self):
        raise NotImplementedError