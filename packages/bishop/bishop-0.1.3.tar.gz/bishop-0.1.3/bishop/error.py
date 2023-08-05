class BuildError(Exception):
    pass
class RoleError(Exception):
    pass
class PackageError(Exception):
    pass
class ConflictError(BuildError):
    pass
class TemplateError(Exception):
    pass

class CalledProcessError(Exception):
    """This exception is raised when a process run by shell() returns
    a non-zero exit status.  The exit status will be stored in the
    returncode attribute and the stderr will be stored in stderr."""
    def __init__(self, returncode, cmd, stderr):
        self.returncode = returncode
        self.cmd = cmd
        self.stderr = stderr
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d: %s" % (self.cmd, self.returncode, self.stderr)
