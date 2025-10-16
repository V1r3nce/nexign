from common.exceptions import NexignBaseException


class StandhelperIsNotParsable(NexignBaseException):
    pass


class StandhelperAppNotFound(NexignBaseException):
    pass


class SSHConnectionNotEstablished(NexignBaseException):
    pass


class SSHNWMTariffsNotReloaded(NexignBaseException):
    pass


class SSHNWMProductOfferingNotFound(NexignBaseException):
    pass
