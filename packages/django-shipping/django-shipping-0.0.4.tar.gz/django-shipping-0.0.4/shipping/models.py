# coding: utf-8
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from shipping.packing.package import Package
from shipping.packing import binpack
from shipping.carriers.correios import CorreiosInterface, CorreiosService
from shipping.carriers.upsinterface import UPSInterface


STATUS = (
    (0, 'Unavailable'),
    (1, 'Available')
)


class Zone(models.Model):
    name = models.CharField(max_length=100)
    status = models.IntegerField(max_length=2, choices=STATUS)
    carrier = models.ForeignKey('Carrier', null=True)

    def get_carrier(self):
        """ get the appropriate carrier class
        """
        carriers_class = ('correioscarrier', 'upscarrier')

        for carrier_class in carriers_class:
            try:
                return getattr(self.carrier, carrier_class)
            except ObjectDoesNotExist:
                pass

    def __unicode__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100)
    iso = models.CharField(max_length=20)
    status = models.IntegerField(max_length=2, choices=STATUS)
    zone = models.ForeignKey(Zone)

    @property
    def needs_full_address(self):
        return self.zone.get_carrier().needs_full_address

    def __unicode__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100)
    iso = models.CharField(max_length=20)
    country = models.ForeignKey(Country, null=True, related_name='states')

    def __unicode__(self):
        return self.name


class Bin(models.Model):
    name = models.CharField(max_length=255)
    width = models.FloatField(help_text="width in centimeters")
    height = models.FloatField(help_text="height in centimeters")
    length = models.FloatField(help_text="length in centimeters")
    weight = models.FloatField(help_text="peso in kilograms")

    carrier = models.ForeignKey('Carrier', related_name='bins')

    def get_package(self):
        return Package((self.height, self.width, self.length))

    def __unicode__(self):
        if self.width and self.height and self.length:
            return "{name} ({w}x{h}x{l})".format(name=self.name, w=self.width,
                h=self.height, l=self.length)

        return self.name


class Carrier(models.Model):
    name = models.CharField(max_length=100)
    status = models.IntegerField(max_length=2, choices=STATUS)

    def estimate_shipping(self, dimensions, country, state, zipcode):
        """ method that finds optimal solution for packing the products
        and according to the zone's carrier calc shipping estimation to zipcode

        :Parameter
          - dimensions: a list of product's dimension '{height}x{width}x{length}x{weight}'
          - zipcode: a valid zip code
          - state: a valid state
        """
        packages = []
        for dimension in dimensions:
            height, width, length, weight = dimension.split('x')
            size = (float(height), float(width), float(length))

            package = Package(size, weight=float(weight))
            packages.append(package)

        best_bin = self.get_best_bin_for_packages(packages)

        if not best_bin:
            raise ValueError('This carrier does not have a valid bin')

        # calc the best packing
        best_packing, rest = binpack(packages, best_bin.get_package())

        total_cost = self.interface.get_shipping_cost(
                bin=best_bin, packages=best_packing, country=country, state=state, zipcode=zipcode)

        return total_cost

    def get_best_bin_for_packages(self, packages):
        """ choose the best bin for a list of packages
        """
        my_packages = []
        for bin in self.bins.all():
            package = bin.get_package()
            package.bin = bin
            my_packages.append(package)

        greater_package = max(packages)
        my_packages.sort()

        for package in my_packages:
            if package.heigth > greater_package.heigth:
                return package.bin

        # when best bin not found, returns de greater bin
        if my_packages:
            return max(my_packages).bin

    def __unicode__(self):
        return self.name


class UPSCarrier(Carrier):
    WEIGHT_UNITS = (
        ('KGS', 'kilograms'),
        ('LBS', 'pounds'),
    )
    DIMENSION_UNITS = (
        ('CM', 'centimeters'),
        ('IN', 'inches'),
    )

    # general
    ups_login = models.CharField(max_length=255, null=True)
    ups_password = models.CharField(max_length=255, null=True)
    ups_id = models.CharField(max_length=255, null=True)
    ups_api_key = models.CharField(max_length=255, null=True)

    # local confs
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_UNITS, default='KGS')
    dimension_unit = models.CharField(max_length=3, choices=DIMENSION_UNITS, default='CM')
    currency_code = models.CharField(max_length=3, default='USD', help_text='ups currency code')

    # sender address
    address_line_1 = models.CharField(max_length=255, null=True)
    address_line_2 = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.ForeignKey(Country, null=True)
    state = models.ForeignKey(State, null=True)

    # services
    RATE_SERVICES = (
        (1, "United States Domestic Shipments"),
        (2, "Shipments Originating in United States"),
        (3, "Shipments Originating in Puerto Rico"),
        (4, "Shipments Originating in Canada"),
        (5, "Shipments Originating in Mexico"),
        (6, "Polish Domestic Shipments"),
        (7, "Shipments Originating in the European Union"),
        (8, "Shipments Originating in Other Countries"),
    )
    rate_service = models.IntegerField(max_length=2, choices=RATE_SERVICES, default=8)

    PICKUP_TYPES = (
        (1, "Daily Pickup"),
        (3, "Customer Counter"),
        (6, "One Time Pickup"),
        (7, "On Call Air"),
        (11, "Suggested Retail Rates"),
        (19, "Letter Center"),
        (20, "Air Service Center")
    )
    pickup_type = models.IntegerField(max_length=2, choices=PICKUP_TYPES, null=True)

    PACKAGES_TYPES = [
        ('02', 'Custom Packaging'),
        ('01', 'UPS Letter'),
        ('03', 'Tube'),
        ('04', 'PAK'),
        ('21', 'UPS Express Box'),
        ('2a', 'Small Express Box'),
        ('2b', 'Medium Express Box'),
        ('2c', 'Large Express Box'),
    ]
    package_type = models.CharField(max_length=3, choices=PACKAGES_TYPES, default='21')

    @property
    def needs_full_address(self):
        return True

    @property
    def interface(self):
        return UPSInterface(self)


class CorreiosCarrier(Carrier):
    correios_company = models.CharField(max_length=200, null=True, help_text='required when using E-Sedex')
    correios_password = models.CharField(max_length=200, null=True, help_text='required when using E-Sedex')
    zip_code = models.CharField(max_length=20, null=True)

    @property
    def needs_full_address(self):
        return False

    @property
    def interface(self):
        return CorreiosInterface(zip_from=self.zip_code, company=self.correios_company,
            password=self.correios_password, service=CorreiosService.SEDEX)
