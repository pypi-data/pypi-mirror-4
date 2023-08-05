=========
pybovespa
=========

The BM&FBOVESPA, in full, Bolsa de Valores, Mercadorias & Futuros de São Paulo)
is a stock exchange located at São Paulo, Brazil.

pybovespa is a basic library to get Bovespa stock values.

Getting and installing
======================

To get pybovespa, please run::

    # pip install pybovespa

Upgrading
=========

To get the new version of currently installed, please run::

    # pip install -U pybovespa

Usage
=====

Its a simple library, so see the example code::

    #!/usr/bin/env python2.7

    from pybovespa.pybovespa import Bovespa

    bovespa = Bovespa()
    paper = bovespa.query("PETR3")
    print paper.cod, paper.name, paper.last

The output should be something like that::

    PETR3 PETROBRAS ON 24,24

