import ast
import sys
import copy
from collections import namedtuple

from rightarrow.annotations import *

class Constraint(object):
    "A type constraint of the form `S <: T`"
    
    def __init__(self, subtype, supertype):
        self.subtype = subtype
        self.supertype = supertype

    def __str__(self):
        return '%s <: %s' % (self.subtype, self.supertype)

    def substitute(self, substitution):
        return Constraint(subtype = self.subtype.substitute(substitution),
                          supertype = self.supertype.substitute(substitution))

class ConstrainedType(object):
    "A type along with a set of constraints, of the form `T & [S1 <: T1, ...]`"
    
    def __init__(self, type=None, constraints=None):
        self.type = type
        self.constraints = constraints or []

class ConstrainedEnv(object):
    """
    An environment mapping variables to types, along with some constraints, and a return type.
    One way to write it might be like...
    
    T_return & { x: T_x, f: T_f, ... } & [S1 <: T1, ...]
    """
    
    def __init__(self, env=None, constraints=None, return_type=None):
        self.env = env or {}
        self.constraints = constraints or []
        self.return_type = return_type

    def substitute(self, substitution):
        return ConstrainedEnv(env = dict([(key, ty.substitute(substitution)) for key, ty in self.env.items()]),
                              constraints = [constraint.substitute(substitution) for constraint in self.constraints],
                              return_type = None if self.return_type is None else self.return_type.substitute(substitution))

    def pretty(self):
        return ("Env:\n\t%(bindings)s\n\nConstraints:\n\t%(constraints)s\n\nResult:\n\t%(result)s" % 
                dict(bindings    = '\n\t'.join(['%s: %s' % (var, ty) for var, ty in self.env.items()]),
                     constraints = '\n\t'.join([str(c) for c in self.constraints]),
                     result      = self.return_type))
    
def constraints(pyast, env=None):
    env = env or {}
    
    if isinstance(pyast, ast.Module) or isinstance(pyast, ast.Interactive):
        env = copy.copy(env)
        constraints = []
        for stmt in pyast.body:
            cs = constraints_stmt(stmt, env=env)
            env.update(cs.env)
            constraints += cs.constraints

        return ConstrainedEnv(env=env, constraints=constraints)

    elif isinstance(pyast, ast.Expression):
        expr_ty = constraints_expr(pyast.body, env=env)
        return ConstrainedEnv(env=env, constraints=expr_ty.constraints)

    else:
        raise Exception('Unknown ast node: %s' % pyast)

def extended_env(env, more_env):
    new_env = copy.copy(env)
    new_env.update(more_env)
    return new_env

# Note that this is rather different in Python 3 - and better!
def fn_env(arguments):
    new_env = {}

    for arg in arguments.args:
        if isinstance(arg, ast.Name) and isinstance(arg.ctx, ast.Param):
            new_env[arg.id] = fresh() # TODO: ??
        else:
            raise Exception('Arg is not a name in Param context!? %s' % arg) 

    if arguments.vararg:
        new_env[arguments.vararg] = fresh() # TODO: sub/superty of list

    if arguments.kwarg:
        new_env[arguments.kwarg] = fresh() # TODO: sub/superty of dict
    
    return new_env

def union(left, right):
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return Union([right, left])

def constraints_stmt(stmt, env=None):
    """
    Since a statement may define new names or return an expression ,
    the constraints that result are in a
    ConstrainedEnv mapping names to types, with constraints, and maybe 
    having a return type (which is a constrained type)
    """
    env = env or {}
    
    if isinstance(stmt, ast.FunctionDef):
        arg_env = fn_env(stmt.args)

        body_env = extended_env(env, arg_env)
        constraints = []
        return_type = None # TODO: should be fresh and constrained?
        for body_stmt in stmt.body:
            cs = constraints_stmt(body_stmt, env=body_env)
            body_env.update(cs.env)
            constraints += cs.constraints
            return_type = union(return_type, cs.return_type)

        env[stmt.name] = Function(arg_types=[arg_env[arg.id] for arg in stmt.args.args],
                                  return_type=return_type)

        return ConstrainedEnv(env=env, constraints=constraints)

    elif isinstance(stmt, ast.Expr):
        constrained_ty = constraints_expr(stmt.value, env=env)
        return ConstrainedEnv(env=env, constraints=constrained_ty.constraints)
        
    elif isinstance(stmt, ast.Return):
        if stmt.value:
            expr_result = constraints_expr(stmt.value, env=env)
            return ConstrainedEnv(env=env, constraints=expr_result.constraints, return_type=expr_result.type)
        else:
            result = fresh()
            return ConstrainedEnv(env=env, constraints=[Constraint(subtype=result, supertype=NamedType('NoneType'))])

    elif isinstance(stmt, ast.Assign):
        if len(stmt.targets) > 1:
            raise NotImplementedError('Cannot generate constraints for multi-target assignments yet')

        expr_result = constraints_expr(stmt.value, env=env)
        target = stmt.targets[0].id
        
        # For an assignment, we actually generate a fresh variable so that it can be the union of all things assigned
        # to it. We do not do any typestate funkiness.
        if target not in env:
            env[target] = fresh()
            
        return ConstrainedEnv(env=env, 
                              constraints = expr_result.constraints + [Constraint(subtype=expr_result.type, 
                                                                                  supertype=env[target])])

    else:
        raise NotImplementedError('Constraint gen for stmt %s' % stmt)
    
def constraints_expr(expr, env=None):
    env = env or {}
    
    if isinstance(expr, ast.Name) and isinstance(expr.ctx, ast.Load):
        if expr.id in ['False', 'True']: # Unlike other literals, these are actually just global identifiers
            return ConstrainedType(type=bool_t)
        elif expr.id in env:
            return ConstrainedType(type=env[expr.id])
        else:
            raise Exception('Variable not found in environment: %s' % expr.id)

    elif isinstance(expr, ast.Num):
        # The python ast module already chose the type of the num
        if isinstance(expr.n, int):
            return ConstrainedType(type=int_t)
        elif isinstance(expr.n, long):
            return ConstrainedType(type=long_t)
        elif isinstance(expr.n, float):
            return ConstrainedType(type=float_t)
        elif isinstance(expr.n, complex):
            return ConstrainedType(type=complex_t)

    elif isinstance(expr, ast.Str):
        return ConstrainedType(type=str_t)

    elif isinstance(expr, ast.List):
        return ConstrainedType(type=List(elem_ty=fresh()))
        
    elif isinstance(expr, ast.BinOp):
        left = constraints_expr(expr.left, env=env)
        right = constraints_expr(expr.right, env=env)
        ty = fresh()
        
        if isinstance(expr.op, ast.Mult):
            # TODO: consider whether all types should match (forces coercions to be explicit; a good thing)
            # Note: though strings and bools can be used in mult, forget it!
            op_constraints = [Constraint(subtype=left.type, supertype=numeric_t),
                              Constraint(subtype=right.type, supertype=numeric_t),
                              Constraint(subtype=ty, supertype=numeric_t)]
        else:
            raise NotImplementedError('BinOp') # TODO: just use function application constraint gen

        # TODO: return type should actually be fancier
        return ConstrainedType(type=ty, constraints=left.constraints+right.constraints+op_constraints)
    else:
        raise NotImplementedError('Constraint gen for %s' % expr)

if __name__ == '__main__':
    with open(sys.argv[1]) as fh:
        proggy = ast.parse(fh.read())

    print ast.dump(proggy)
        
    print constraints(proggy).pretty()
