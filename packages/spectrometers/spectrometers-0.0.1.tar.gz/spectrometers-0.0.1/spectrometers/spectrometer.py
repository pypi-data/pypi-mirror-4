# -*- coding: utf-8 -*-

class Spectrometer(object):
    """
    Exposes a simple API for spectrometers/spectrophotometers.
    """

    def __init__(self):
        object.__init__(self)

    def capture(self):
        """
        Returns a list of wavelengths that were captured in this session.
        """
        raise NotImplementedError("can't be called from super")

