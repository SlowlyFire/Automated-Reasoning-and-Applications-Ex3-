# importing classes from pysmt for utility functions
from pysmt.walkers import IdentityDagWalker
from pysmt.walkers.generic import handles
import pysmt.operators as op
from pysmt.shortcuts import get_env
from pysmt.shortcuts import And

# helper class
class SubTermsGetter(IdentityDagWalker):
  def __init__(self, env):
    IdentityDagWalker.__init__(self, env=env, invalidate_memoization=True)
    self.sub_terms = set([])
  
  @handles(set(op.ALL_TYPES))
  def walk_collect(self, formula, args, **kwargs):
    self.sub_terms.add(formula)

# helper class
class FunctionSymbolsGetter(IdentityDagWalker):
  def __init__(self, env):
    IdentityDagWalker.__init__(self, env=env, invalidate_memoization=True)
    self.funs = set([])
  
  def walk_function(self, formula, args, **kwargs):
    function_name = formula.function_name()
    self.funs.add(function_name)
  
  @handles(set(op.ALL_TYPES) - set([op.FUNCTION]))
  def default(self, formula, args, **kwargs):
    return formula


# Utility Functions

# get all terms in a cube.
# for example: get_terms([x=y, f(x)=z]) = [x, y, z, f(x)]
def get_terms(cube):
  formula = And(cube)
  sub_terms_getter = SubTermsGetter(get_env())
  sub_terms_getter.walk(formula)
  return [t for t in sub_terms_getter.sub_terms if t.is_symbol() or t.is_function_application()]

# get all function symbols in a cube.
# for example: get_function_symbols([x=y, f(x)=z]) = [z]
def get_function_symbols(cube):
  formula = And(cube)
  function_symbols_getter = FunctionSymbolsGetter(get_env())
  function_symbols_getter.walk(formula)
  return function_symbols_getter.funs

# check if `cube` is indeed a cube (that is, a list of literals)
def is_cube(cube):
  for lit in cube:
    if not is_lit(lit):
      return False
  return True

# check if `term` is a literal (equality or negation of equality)
def is_lit(term):
  return term.is_equals() or (term.is_not() and term.args()[0].is_equals())

# check if `lit` is a flat literal
def is_flat_lit(lit):
  assert is_lit(lit)
  if lit.is_equals():
    left = lit.args()[0]
    right = lit.args()[1]
    if not left.is_symbol():
      return False
    if right.is_symbol():
      return True
    assert right.is_function_application()
    if right.args()[0].is_symbol():
      return True
    else:
      return False
  else:
    assert lit.is_not() and lit.args()[0].is_equals()
    eq = lit.args()[0]
    left = eq.args()[0]
    right = eq.args()[1]
    return left.is_symbol() and right.is_symbol()

# check if `cube` is a flat cube
def is_flat_cube(cube):
  if not is_cube(cube):
    return False
  for lit in cube:
    if not is_flat_lit(lit):
      return False
  return True