# -*- coding: utf-8 -*-
"""
Functions of initialization  layers

"""


import numpy as np


def init_rand(layer, min=-0.5, max=0.5, init_prop='w'):
    """
    Initialize the specified property of the layer
    random numbers within specified limits

    :Parameters:
        layer:
            Initialized layer
        min: float (default -0.5)
            minimum value after the initialization
        max: float (default 0.5)
            maximum value after the initialization
        init_prop: str (default 'w')
            name of initialized property, must be in layer.np

    """

    if init_prop not in layer.np:
        raise ValueError('Layer not have attibute "' + init_prop + '"')
    layer.np[init_prop] = np.random.uniform(min, max, layer.np[init_prop].shape)

def initwb_reg(layer):
    """
    Initialize weights and bias
    in the range defined by the activation function (transf.inp_active)

    """
    active = layer.transf.inp_active[:]

    if np.isinf(active[0]):
        active[0] = -100.0

    if np.isinf(active[1]):
        active[1] = 100.0

    min = active[0] / (2 * layer.cn)
    max = active[1] / (2 * layer.cn)

    init_rand(layer, min, max, 'w')
    if 'b' in layer.np:
        init_rand(layer, min, max, 'b')


class InitRand:
    """
    Initialize the specified properties of the layer
    random numbers within specified limits

    """
    def __init__(self, minmax, init_prop):
        """
        :Parameters:
            minmax: list of float
                [min, max] init range
            init_prop: list of dicts
                names of initialized propertis. Example ['w', 'b']

        """
        self.min = minmax[0]
        self.max = minmax[1]
        self.properties = init_prop

    def __call__(self, layer):
        for property in self.properties:
            init_rand(layer, self.min, self.max, property)
        return


def init_zeros(layer):
    """
    Set all layer properties of zero

    """
    for k in layer.np:
        layer.np[k].fill(0.0)
    return


def midpoint(layer):
    """
    Sets weight to the center of the input ranges

    """
    mid = layer.inp_minmax.mean(axis=1)
    for i, w in enumerate(layer.np['w']):
        layer.np['w'][i] = mid.copy()
    return
