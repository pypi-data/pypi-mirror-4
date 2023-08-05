import numpy as np
from .core import Operator, BlockRowOperator, CompositionOperator
from .utils import MPI

# these function may be overridden
sum = np.sum
dot = np.dot

class NormOperator(Operator):
    commin = None
    commout = MPI.COMM_SELF
    shapeout = ()
    operation = 'sum'
    def __init__(self, **keywords):
        Operator.__init__(self, **keywords)
        self.set_rule('.{BlockOperator}', lambda s,b:s._rule_block(s,b), 
                      CompositionOperator)

    @staticmethod
    def _rule_block(self, b):
        if b.partitionout is None:
            return
        s = self.copy()
        s.commin = None
        return BlockRowOperator(len(b.partitionout) * s, operation='sum',
                                partitionin=b.partitionout, axisin=b.axisout,
                                new_axisin=b.new_axisout, commin=b.commout,
                                commout=self.commout) * b

class Norm2Operator(NormOperator):
    def direct(self, input, output):
        output[...] = dot(input, input)
        if self.commin is not None:
            self.commin.Allreduce(MPI.IN_PLACE, output)
