from random import random, choice,sample
from math import log
from inspect import isclass
from itertools import islice

__generators__ = {}

DEFAULT_GENERATOR_SIZE=10

def generates(typ):
    def accept_function(fn):
        define_generator_for(typ, fn)
        return fn
    return accept_function

def generator(typ):
    if not typ:
        raise ValueError("generator requires at least one type argument")

    if isclass(typ):
        return __generators__[typ]
    elif isinstance(typ,tuple):
        return tuple_generator(map(generator, typ))
    elif isinstance(typ, list):
        if not typ:
            raise ValueError("Array arguments must be non-empty")
    
        gen = one_of(*map(generator,typ)) 
        return list_generator(gen)   
    elif isinstance(typ,dict):
        return dict_generator(typ)
    else:
        raise ValueError("I don't understand the argument %typ")

def generate(typs, size=DEFAULT_GENERATOR_SIZE,):
    if size <= 0 or not isinstance(size,int):
        raise ValueError("Size  %s should be a positive integer" % size)

    return generator(typs)(size)

def define_generator_for(t, m):
    __generators__[t] = m

def tuple_generator(tup):
    def gen(size):
        generators = [g(size) for g in tup]
        while True:
            yield tuple((g.next() for g in generators))
    return gen

def list_generator(elements):
    def gen(size):
        element_generator = elements(size)
        length_generator = generate(int, size)
        while True:
            length = abs(length_generator.next())
            yield list(islice(element_generator, length))
    return gen

def dict_generator(generator_dict):
    def gen(size):
        generators = [(k,generator(v)(size)) for (k,v) in generator_dict.items()]
        while True:
            result = {}
            for k,g in generators:
                result[k] = g.next()
            yield result
    return gen

def repeatedly_yield(f):
    def gen(size):
        while True:
            yield f(size)
    return gen

def one_of(*args):
    """
    Takes n generators as arguments, returns a generator which calls each
    with equal probability
    """
    if len(args) == 1:
        return args[0]
    def gen(size):
        generators = map(lambda a: a(size), args)
        while True:
            yield choice(generators).next()
    return gen

def random_float(size):
    if random() <= 0.05:
        if flip_coin():
            return -0.0
        else:
            return 0.0
    else:
        x = -log(random()) * size
        if flip_coin():
            x = 1/x
        if flip_coin():
            x = -x
    return x

def geometric_int(size):
    """
    Generate a geometric integer with expected absolute value size and sign
    negative or positive with equal probability
    """
    p = 1.0 / (size + 1)
    n =  int(log(random()) / log(1 - p))
    if random() <= 0.5:
        n = -n
    return n

characters = map(chr,range(0,127))

@generates(str)
def generate_string(size):
    length_generator = generate(int,size)
    for l in length_generator:
        yield ''.join((choice(characters) for _ in xrange(l)))

def flip_coin():
    return random() <= 0.5

define_generator_for(int, repeatedly_yield(geometric_int))
define_generator_for(float, repeatedly_yield(random_float))
