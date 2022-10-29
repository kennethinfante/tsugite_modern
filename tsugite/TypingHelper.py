from typing import Any, Optional, Union
from numpy.typing import ArrayLike, DTypeLike
from OpenGL.constant import Constant as glConstant

# aliases
DegreeArray = ArrayLike         # for the return joint_type of arccos
ZeroArray = ArrayLike
DotProduct = ArrayLike          # Returns the dot product of a and b. If both are scalars or both are 1-D arrays then
                                # a scalar is returned; otherwise an array is returned.

FilePath = str
FabricationExt = str            # either "gcode", "nc", "sbp"
DrawTypes = glConstant          # GL_QUADS, GL_LINES, GL_TRIANGLES, GL_LINE_STRIP
Direction = int                 # 1 for positive, 0 for negative direction
FxSide = int                    # Implementation refers to 'Fixed Sides' as which of the six sides of the joint are
                                # connected to the main body of the timber. One fixed side indicates that the joint is located at the
                                # end of a timber, which is the case for the timbers of an L-joint.
                                # Two fixed sides means that the joint is located somewhere in
                                # the middle of the timber, as for the timbers of an X-joint.