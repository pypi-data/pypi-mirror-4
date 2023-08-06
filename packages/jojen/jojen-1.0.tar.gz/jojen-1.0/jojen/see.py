import os

not_equal = object()          # I just want something nothing else is equal to

DEFAULT_INTERPRETATION_ERROR = "The gods' message '%(name)s' had the value \
'%(value)s'. It didn't fit this interpretation."

def ensure_interpretation(value, name, interpreter,
                          interpretation_error=DEFAULT_INTERPRETATION_ERROR):
  try:
    return interpreter(value)
  except ValueError as ve:
    raise Exception(interpretation_error % {"value": value, "name": name})

def see_interpretation(name, interpreter, default=not_equal,
                       interpretation_error=DEFAULT_INTERPRETATION_ERROR):
  return ensure_interpretation(see(name, default=default), name, interpreter,
                               interpretation_error=interpretation_error)

NUMBER_INTERPRETATION_ERROR = "The gods' message '%(name)s' was not a number. \
Its value was '%(value)s'."

def ensure_number(value, name):
  return ensure_interpretation(value, name, int, interpretation_error=NUMBER_INTERPRETATION_ERROR)

def see_number(name, default=not_equal):
  return ensure_number(see(name, default=default), name)

def strict_bool_interpretation(value):
  if isinstance(value, bool):
    return value
  if value == "True":
    return True
  elif value == "False":
    return False
  else:
    raise ValueError("'%s' isn't a boolean." % value)

BOOLEAN_INTERPRETATION_ERROR = "The gods' message '%(name)s' was not a boolean. \
Its value was '%(value)s'."

def ensure_boolean(value, name):
  return ensure_interpretation(value, name, strict_bool_interpretation,
                               interpretation_error=BOOLEAN_INTERPRETATION_ERROR)

def see_boolean(name, default=not_equal):
  return ensure_boolean(see(name, default=default), name)

def ensure_sequence(value):
  if isinstance(value, tuple):
    return value
  else:
    return tuple(value.split(","))

def see_sequence(name, default=not_equal):
  return ensure_sequence(see(name, default=default))

def see(name, default=not_equal):
  if name in os.environ:
    return os.environ[name]
  elif default != not_equal:
    return default
  else:
    raise Exception("The gods say nothing of a message named '%s'." % name)
