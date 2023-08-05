#!/usr/bin/env python2.6
import sys
import urllib2
import xml.etree.ElementTree as ET

BOVESPA_URL = "http://www.bmfbovespa.com.br/Pregao-Online/ExecutaAcaoAjax.asp?CodigoPapel=%s"

class BovespaError(Exception):
    """A Bovespa exception class."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Bovespa():
    """A generic Bovespa class."""

    def __init__(self):
        pass

    def query(self, cod):
        paper = Paper(cod)
        return paper

class Paper():
    """A generic Paper class."""

    def __init__(self, cod):
        self.cod = cod
        self.update()

    def __str__(self):
        return repr(self.name, self.cod)

    def update(self):
        url = BOVESPA_URL % self.cod

        # Try to connect to bovespa url and get a xml file
        try:
            tree = ET.parse(urllib2.urlopen(url))
        except Exception, e:
            raise BovespaError(e)

        # Parse xml
        try:
            root = tree.getroot()
            child = root._children[0]
            paper = child.attrib
            self.name = paper.get('Nome')
            self.date = paper.get('Data')
            self.opening = paper.get('Abertura')
            self.min = paper.get('Minimo')
            self.max = paper.get('Maximo')
            self.avg = paper.get('Medio')
            self.last = paper.get('Ultimo')
            self.oscillation = paper.get('Oscilacao')
        except Exception, e:
            raise BovespaError(e)
