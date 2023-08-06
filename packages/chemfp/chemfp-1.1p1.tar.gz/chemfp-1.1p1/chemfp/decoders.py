import warnings

warnings.warn("The decoders are now located in the chemfp.encoders module.", DeprecationWarning)

from .encodings import (from_base64, from_binary_lsb, from_binary_msb, from_cactvs, from_daylight,
                        from_hex, from_hex_lsb, from_hex_msb, from_on_bit_positions)
1/0
