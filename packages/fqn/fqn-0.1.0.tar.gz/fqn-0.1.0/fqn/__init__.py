
def get_object(fullname):
  """
  This function retrieves a specific object from a module
  without polluting the current namespace.
  
    q = get_object("foo.bar.quux")
    
  is equivalent to:
  
    from foo.bar import quux as q
    
  """
  components = fullname.split(".")

  # Find the module boundary
  for x in xrange(len(components), 0, -1):
    try:
      obj = __import__(".".join(components[0:x]), level = 0)
      break
    except ImportError:
      pass
  else:
    raise ImportError("cannot import " + fullname)
  
  
  # Crawl the object model to find the desired object
  try:
    for c in components[1:]:
      obj = getattr(obj, c)
  except AttributeError:
    raise ImportError("cannot import " + fullname)
  
  return obj


def get_fullname(object):
  """
  Returns the full name for the given object.  The object must
  define both the __name__ and __module__ attributes.
  """
  return "%s.%s" % (object.__module__, object.__name__)



def _defined_by(module):
  for name in dir(module):
    o = getattr(module, name)
    if hasattr(o, "__module__") and o.__module__ == module.__name__:
      yield name

def defined_by(module):
  """
  Returns the list of objects that were actually defined by the
  specified module.  In other words: this will not list the objects
  that were imported from other modules.
  """
  return list(_defined_by(module))



def _imported_by(module):
  for name in dir(module):
    o = getattr(module, name)
    if hasattr(o, "__module__") and o.__module__ != module.__name__:
      yield name


def imported_by(module):
  return list(_imported_by(module))