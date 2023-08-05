import sys

if sys.version_info[0] == 2:

    from immutable.core_py2 import Immutable, immutable, \
         ImmutableTuple, ImmutableSet, ImmutableDict, \
         register_immutable_converter

else:

    from immutable.core_py3 import Immutable, immutable, \
         ImmutableTuple, ImmutableSet, ImmutableDict, \
         register_immutable_converter
