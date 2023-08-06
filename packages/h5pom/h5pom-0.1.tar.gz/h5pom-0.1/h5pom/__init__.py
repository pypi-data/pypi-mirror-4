from core import open, IN_MEMORY, loader_key, \
        Folder, Object, Duplicator

from descriptors import Scalar, Array, SubObject, \
                        ScalarList, SubObjectList, \
                        SubObjectDict # NOTE:  ScalarDict is not supported due to confusion over persistence in attributes

__version_info__ = ['0', '1']
__version__ = '.'.join(__version_info__)
