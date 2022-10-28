from typing import Any, Optional
from numpy.typing import ArrayLike, DTypeLike
from OpenGL.constant import Constant as glConstant

# aliases
DegreeArray = ArrayLike            # for the return type of arccos
ZeroArray = ArrayLike
DotProduct = ArrayLike             # Returns the dot product of a and b. If both are scalars or both are 1-D arrays then
                                   # a scalar is returned; otherwise an array is returned.

FilePath = str
DrawTypes = glConstant             # GL_QUADS, GL_LINES, GL_TRIANGLES, GL_LINE_STRIP