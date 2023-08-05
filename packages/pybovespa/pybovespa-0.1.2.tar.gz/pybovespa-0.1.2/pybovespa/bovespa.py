import sys
import os
import errno
import zipfile
import urllib3
import xml.etree.ElementTree as ET

from datetime import datetime, time, date, timedelta
from pybovespa.stock import *
from pybovespa.exceptions import *


class Bovespa():
    """A generic Bovespa class.

    This class is responsible for talking directly with the Bovespa webservices
    via REST. Its is very simple.
    """

    bovespa_host = 'http://www.bmfbovespa.com.br'
    cotault_url = '/Pregao-Online/ExecutaAcaoAjax.asp'
    stock_param = 'CodigoPapel'
    cotahist_url = '/InstDados/SerHist/COTAHIST_A%s.zip'

    def __init__(self):
        pass

    def query(self, *codes):
        # Only one request for many stocks
        xml = self.get_xml(*codes)
        stocks = self.get_stocks(xml, *codes)

        if len(stocks) == 1:
            answer = stocks[codes[0]]
        else:
            answer = stocks

        return answer

    def decode(self, bytes):
        output = bytes.decode('latin-1').strip()
        return output

    def get_stocks(self, xml, *codes):
        stocks = []

        root = ET.fromstring(xml)
        for code in codes:
            # Parse xml
            try:
                child = root.find(".//*[@Codigo='%s']" % code)
                stock_xml = child.attrib
                data = stock_xml.get('Data')
                data = datetime.strptime(data, '%d/%m/%Y %H:%M:%S')
                stock = Stock(data, code)
                stock.nomeres = stock_xml.get('Nome')
                stock.preabe = stock_xml.get('Abertura')
                stock.premin = stock_xml.get('Minimo')
                stock.premax = stock_xml.get('Maximo')
                stock.premed = stock_xml.get('Medio')
                stock.preult = stock_xml.get('Ultimo')
                stocks.append(stock)
            except Exception as e:
                raise BovespaError(e)

        return stocks

    def get_xml(self, *codes):
        # Try to connect to bovespa url and get a xml file
        try:
            http_pool = urllib3.connection_from_url(self.bovespa_host)
            fields = {self.stock_param: '|'.join(codes)}
            response = http_pool.request("GET", self.cotault_url, fields)
        except Exception as e:
            raise BovespaError(e)

        return response.data

    def download(self, dst, year, overwrite):
        dst = "%s/compressed" % dst
        try:
            os.makedirs(dst)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        url = self.cotahist_url % year
        try:
            http_pool = urllib3.connection_from_url(self.bovespa_host)
            response = http_pool.request("GET", url)
        except Exception as exception:
            raise

        output = "%s/COTAHIST_A%s.zip" % (dst, year)
        if (not os.path.exists(output)) or overwrite:
            try:
                with open(output, "wb") as code:
                    code.write(response.data)
            except Exception as exception:
                raise

        return output

    def download_all(self, dst, overwrite):
        now = datetime.datetime.now().year
        files = []
        for year in range(1996, now+1):
            files.appen(self.download(dst, year, overwrite))

        return files

    def load_from_file(self, file):
        zfobj = zipfile.ZipFile(file)
        stocks = []
        for name in zfobj.namelist():
            for line in zfobj.open(name):
                tipreg = self.decode(line[0:2])
                if tipreg == '01':
                    tpmerc = self.decode(line[24:27])
                    if tpmerc in ('010', '020'):
                        data = datetime.strptime(self.decode(line[2:10]), '%Y%m%d')
                        codneg = self.decode(line[12:24])
                        nomres = self.decode(line[27:39])
                        #modref = self.decode(line[52:56])
                        preabe = self.decode(line[56:59])
                        premax = self.decode(line[69:82])
                        premin = self.decode(line[82:95])
                        premed = self.decode(line[95:108])
                        preult = self.decode(line[108:121])
                        stock = Stock(data, codneg)
                        stocks.append(stock)
        zfobj.close()
        return stocks
