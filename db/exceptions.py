from common.exceptions import NexignBaseException


class StandhelperIsNotParsable(NexignBaseException):
    pass


class DBCreditsNotFound(NexignBaseException):
    pass


class DBConnectionNotEstablished(NexignBaseException):
    pass


class DBInvalidSQLQuery(NexignBaseException):
    pass
