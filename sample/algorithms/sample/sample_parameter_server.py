from relaax.server.common.session import Session
from sample_ps_model import PSModel
from relaax.server.parameter_server.parameter_server_base import (
    ParameterServerBase)


class SampleParameterServer(ParameterServerBase):
    def __init__(self):
        self.session = Session(PSModel())
        self.session.run([self.session.model.initialize])