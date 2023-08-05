#coding: utf-8
from shipping.carriers import InterfaceError
import logging
import urllib2
import urllib
import simplexml
import math

logger = logging.getLogger(__name__)


class CorreiosFormat:
    """enumerate available correios formats
    """
    PACOTE = 1
    ROLO = 2


class CorreiosService:
    """enumerate available correios services
    """
    PAC = '41106'
    SEDEX = '40010'
    SEDEX10 = '40215'
    SEDEXHOJE = '40290'
    SEDEXCOBRAR = '40045'


class CorreiosInterface(object):
    """implements basic integration with federal brazilian carrier, Correios.
    """
    _endpoint = 'http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx'
    _min_dimensions = {
        CorreiosFormat.PACOTE: (18, 5, 0, 0),
        CorreiosFormat.ROLO: (16, 0, 2, 5)
    }

    def __init__(self, zip_from, company=None, password=None,
        service=CorreiosService.SEDEX, format=CorreiosFormat.PACOTE):
        """create a new instance of correios carrier

        :Parameters
          - zip_from: zipcode of where package will be delivered
          - password: correios company password
          - company: correios company code
          - service: correios service
          - format: format of package
        """
        self._zip_from = zip_from
        self._password = password
        self._company = company
        self._service = service
        self._format = format

        self._length = None
        self._diameter = None
        self._height = None
        self._width = None
        self._zip_to = None

        self._aviso_recebimento = 'N'
        self._valor_declarado = 0
        self._mao_propria = 'N'

    def _get_diameter(self):
        """returns the diameter of the sphere inscrit in the package
        """
        return int(math.sqrt(math.pow(self._length, 2) +
            math.pow(self._width, 2)))

    def _set_dimensions(self, package, weight_total):
        self._length, self._diameter, self._height, self._width = self._min_dimensions.get(self._format)
        self._weight = 0.3

        if package.height > self._height:
            self._height = package.height

        if package.width > self._width:
            self._width = package.width

        if package.length > self._length:
            self._length = package.length

        if weight_total > self._weight:
            self._weight = weight_total

        # height can't be greater than length
        if self._height > self._length:
            self._height = self._length

        # width can't be less than 11cm when length is less than 25cm
        if self._format == CorreiosFormat.PACOTE and self._width < 11 \
            and self._length < 25:
            self._width = 11

        # set diameter
        diameter = self._get_diameter()
        if diameter > self._diameter:
            self._diameter = diameter

    def _get_parameters(self):
        params = {
            'nCdEmpresa': self._company,
            'sDsSenha': self._password,
            'strRetorno': 'xml',
            'sCdMaoPropria': self._mao_propria,
            'nVlValorDeclarado': self._valor_declarado,
            'sCdAvisoRecebimento': self._aviso_recebimento,
            'nCdFormato': self._format,
            'sCepOrigem': self._zip_from,
            'sCepDestino': self._zip_to,
            'nCdServico': self._service,
            'nVlAltura': int(self._height),
            'nVlLargura': int(self._width),
            'nVlComprimento': int(self._length),
            'nVlDiametro': int(self._diameter),
            'nVlPeso': str(self._weight).replace('.', ',')
        }

        return params

    def _make_request(self):
        params = self._get_parameters()
        url = '%s?%s' % (self._endpoint,
            urllib.urlencode(params))

        logger.debug('estimating freight on correios')
        logger.debug(params)

        data = urllib2.urlopen(url, timeout=5).read()

        """
        Exemplo do retorno:
            <cServico>
                <Codigo>40045</Codigo>
                <Valor>12,10</Valor>
                <PrazoEntrega>1</PrazoEntrega>
                <ValorMaoPropria>0,00</ValorMaoPropria>
                <ValorAvisoRecebimento>0,00</ValorAvisoRecebimento>
                <ValorValorDeclarado>1,00</ValorValorDeclarado>
                <EntregaDomiciliar>S</EntregaDomiciliar>
                <EntregaSabado>S</EntregaSabado>
                <Erro>0</Erro>
                <MsgErro></MsgErro>
            </cServico>
        """
        logger.debug('response from correios')
        logger.debug(data)

        response = simplexml.loads(data)

        result = response['Servicos']['cServico']

        erro = int(result.get('Erro'))
        if erro != 0:
            raise InterfaceError(result.get('MsgErro'))
        else:
            return result.get('Valor')

    def get_shipping_cost(self, bin, packages, country, zipcode, state=None, city=None):
        self._zip_to = zipcode

        total_cost = 0.0
        for pack in packages:
            # calc total weight, sum of all packages plus bin weight
            weight_total = sum([package.weight for package in pack]) + bin.weight

            # calc shipping price for each pack
            self._set_dimensions(bin, weight_total)

            price = self._make_request()
            total_cost += float(price.replace(',', '.'))

        return total_cost, 'BRL'
