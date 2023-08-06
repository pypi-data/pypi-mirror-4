class ServerError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

class CloudError(ServerError):
    pass

class VolumeError(CloudError):
    pass

class NetworkError(ServerError):
    pass

class SecurityError(ServerError):
    pass

class ClientError(Exception):
    def __init__(self, arg, code=None):
        self.arg = arg
        self.code = code

    def __str__(self):
        return self.arg

class AbortException(ClientError):
    pass

class NotFoundError(ClientError):
    pass

class NotYetSetException(ClientError):
    pass

class ConfigurationError(ClientError):
    pass

class TimeoutException(ClientError):
    pass

class TerminalStateException(ClientError):
    pass

class ExecutionException(ClientError):
    pass

class ParameterNotFoundException(ClientError):
    pass
