# -*- coding: utf-8 -*-
"""
This file is part of the charset python package
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
__author__ = "Karel Antonio Verdecia Ortiz"
__contact__ = "kverdecia@uci.cu"

import chardet

cdef extern from "mozilladetector/detector.h":
    
    cdef cppclass CharSetDetector:
        CharSetDetector(int language_filter) nogil
        int HandleData(char* aBuf, int aLen) nogil
        void DataEnd() nogil
        char *DetectedCharset() nogil
        
        
cdef class Detector:
    """Clase base para la detección de codificación de carateres. Utiliza el
    paquete chardet.
    """
    def detect(self, bytes text):
        """Detecta la codificacion de carateres del texto que se pasa por 
        parámetro.
        :param text: Texto que se va a analizar.
        :type text: `str`
        :return: Devuelve la codificación detectada.
        :rtype: `str`
        """
        cdef bytes result = chardet.detect(text)['encoding']
        if result is None:
            return "ascii"
        return result.lower()
        
        
cdef class MozDetector(Detector):
    def detect(self, bytes text):
        """Detecta la codificacion de carateres del texto que se pasa por 
        parámetro.
        :param text: Texto que se va a analizar.
        :type text: `str`
        :return: Devuelve la codificación detectada.
        :rtype: `str`
        """
        cdef CharSetDetector *detector = new CharSetDetector(31)
        cdef char *ptext = text
        cdef char *encoding
        cdef int length = len(text)
        cdef bytes result
        with nogil:
            detector.HandleData(ptext, length)
            detector.DataEnd()
            encoding = detector.DetectedCharset()
            if encoding == NULL:
                encoding = "ascii"
        result = encoding 
        del detector
        return result.lower()


cdef class CheckDetector(Detector):
    cdef MozDetector moz_det
    cdef dict cache
    
    def __init__(self):
        self.moz_det = MozDetector()
        self.cache = dict()
        
    def detect(self, bytes text):
        """Detecta la codificacion de carateres del texto que se pasa por 
        parámetro.
        :param text: Texto que se va a analizar.
        :type text: `str`
        :return: Devuelve la codificación detectada.
        :rtype: `str`
        """
        cdef bytes encoding = self.moz_det.detect(text)
        cdef bytes new_encoding
        try:
            text.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            pass
        if encoding in self.cache:
            new_encoding = self.cache[encoding]
            try:
                text.decode(new_encoding)
                return new_encoding
            except UnicodeDecodeError:
                pass
        new_encoding = Detector.detect(self, text)
        if new_encoding is None:
            raise ValueError("Unknown encoding.")
        self.cache[encoding] = new_encoding
        return new_encoding
        
        