import os
from gears.compressors import ExecCompressor


class CleanCSSCompressor(ExecCompressor):

    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'compressor.js')]
