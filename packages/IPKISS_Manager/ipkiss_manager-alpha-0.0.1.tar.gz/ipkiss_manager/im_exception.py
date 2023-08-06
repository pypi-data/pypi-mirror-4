
class TimeoutError(BaseException):
    pass


class UnsolvableError(BaseException):
    pass


class ReferenceFileError(BaseException):
    pass


class DownloadError(BaseException):
    pass


class ShapelyNotInstalled(BaseException):
    pass


class DependencyError(BaseException):
    pass


class VersionError(BaseException):
    pass


class RemoveError(BaseException):
    """
        Errors on removing IPKISS
    """

class RemoveByVersionError(RemoveError):
    pass

class RemoveByPathError(RemoveError):
    pass

class PermissionError(BaseException):
    pass

class UnkowIpkissRelease(BaseException):
    pass
