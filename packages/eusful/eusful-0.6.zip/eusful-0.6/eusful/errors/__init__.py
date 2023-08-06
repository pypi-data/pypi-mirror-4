import logging
import sys
import traceback
import web

def printerrors(function):
  def wrapped(*a, **kw):
    try:
      return function(*a, **kw)
    except web.Redirect:
      raise
    except Exception as e:
      logging.exception(e.message)
      traceback.print_exception(*sys.exc_info())
  return wrapped
