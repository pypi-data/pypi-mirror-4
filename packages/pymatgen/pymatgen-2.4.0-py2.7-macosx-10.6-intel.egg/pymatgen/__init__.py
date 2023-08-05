__author__ = "Shyue Ping Ong, Anubhav Jain, Michael Kocher, " + \
             "Geoffroy Hautier, William Davidson Richard, Dan Gunter, " + \
             "Shreyas Cholia, Vincent L Chevrier, Rickard Armiento"
__date__ = "Jan 4 2013"
__version__ = "2.4.0"

#Useful aliases for commonly used objects and modules.

from pymatgen.core.periodic_table import Element, Specie
from pymatgen.core.composition import Composition
from pymatgen.core.structure import Structure, Molecule
from pymatgen.core.lattice import Lattice
from pymatgen.serializers.json_coders import PMGJSONEncoder, PMGJSONDecoder
from pymatgen.electronic_structure.core import Spin, Orbital
from pymatgen.util.io_utils import zopen
