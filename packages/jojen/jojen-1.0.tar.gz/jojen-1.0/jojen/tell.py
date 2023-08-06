from see import *

def tell(name, default=not_equal):
  return lambda: see(name, default=default)

def tell_number(name, default=not_equal):
  return lambda: see_number(name, default=default)

def tell_boolean(name, default=not_equal):
  return lambda: see_boolean(name, default=default)

def tell_sequence(name, default=not_equal):
  return lambda: see_sequence(name, default=default)

def tell_interpretation(name, interpreter, default=not_equal):
  return lambda: see_interpretation(name, interpreter, default=default)
