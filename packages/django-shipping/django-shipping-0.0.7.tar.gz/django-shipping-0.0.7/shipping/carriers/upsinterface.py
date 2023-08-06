# coding: utf-8
from ups.client import UPSClient, UPSError
from ups.model import Address, Package as UPSPackage
from shipping.carriers import InterfaceError


class UPSInterface(object):

    def __init__(self, ups_carrier):

        credentials = {
            'username': ups_carrier.ups_login,
            'password': ups_carrier.ups_password,
            'access_license': ups_carrier.ups_api_key,
            'shipper_number': ups_carrier.ups_id,
        }
        self.shipper = Address(name='shipper address name', city=ups_carrier.city,
            address=ups_carrier.address_line_1, state=ups_carrier.state.iso,
            zip=ups_carrier.zip_code, country=ups_carrier.country.iso,
            address2=ups_carrier.address_line_2)

        self.ups = UPSClient(credentials, weight_unit=ups_carrier.weight_unit,
            dimension_unit=ups_carrier.dimension_unit, currency_code=ups_carrier.currency_code)

        self.package_type = ups_carrier.package_type

    def get_shipping_cost(self, bin, packages, country, zipcode=None, state=None, city=None):

        ups_packages = []
        for pack in packages:
            weight_total = sum([package.weight for package in pack]) + bin.weight

            ups_packages.append(UPSPackage(weight=weight_total, length=bin.length,
            width=bin.width, height=bin.height))

        state_iso = state.iso if state else None
        city = city or ''
        zipcode = zipcode or ''
        recipient = Address(name='recipient address name', city=city,
            address='', zip=zipcode, country=country.iso, state=state_iso)

        try:
            rate_result = self.ups.rate(ups_packages, self.shipper, recipient, self.package_type)
        except UPSError, e:
            raise InterfaceError(str(e))

        return rate_result['info'][0]['cost'], rate_result['info'][0]['currency']
