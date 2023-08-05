from   StringIO   import StringIO
from   subprocess import Popen, PIPE
from   types      import StringTypes
import mock
import logging

log = logging.getLogger(__name__)


def stream_for(input):
  """
  If the input is a string, then return a StringIO instance.
  Otherwise, just return the original input.  (In other words:
  just assume the input is a stream)
  """
  if isinstance(input, StringTypes):
    return StringIO(input)
  else:
    return input


class Popen_Mock(object):
  def __init__(self, stdout = '', stderr = '', result = 0):
    self.stdout = stdout
    self.stderr = stderr
    self.result = 0

  def __call__(self, args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, *leftover_args, **kwargs):
    retval = mock.MagicMock()

    retval.stdout = stream_for(self.stdout) if stdout == PIPE else None
    retval.stderr = stream_for(self.stderr) if stderr == PIPE else None

    def communicate(stdin = None):
      o = retval.stdout.read() if retval.stdout else None
      e = retval.stderr.read() if retval.stderr else None
      return (o, e)
    
    retval.communicate.side_effect = communicate
    
    retval.wait.return_value = self.result
    return retval



class Popen_LogArguments(object):
  def __init__(self, popen, log = log, level = logging.DEBUG, log_args = None, log_kwargs = None):
    self.popen = popen
    self.log   = log
    self.level = level
    self.log_args   = log_args   if log_args   else []
    self.log_kwargs = log_kwargs if log_kwargs else {}

  def __call__(self, *args, **kwargs):
    self.log.log(self.level, "args:   %s",   args, *self.log_args, **self.log_kwargs)
    self.log.log(self.level, "kwargs: %s", kwargs, *self.log_args, **self.log_kwargs)
    
    return self.popen(*args, **kwargs)
