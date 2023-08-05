name = 'relimp.B.C'

from . import D                 # Imports relimp.B.D
from .D import X                 # Imports relimp.B.D.X
from .. import E                # Imports relimp.E
from ..F import G               # Imports relimp.F.G
from ..F import H               # Imports relimp.F.H

assert D.name == 'relimp.B.D'
assert E.name == 'relimp.E'
assert G.name == 'relimp.F.G'
assert H.name == 'relimp.F.H'
