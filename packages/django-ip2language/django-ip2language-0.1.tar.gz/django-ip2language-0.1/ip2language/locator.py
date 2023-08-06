from django.conf import settings

from pygeoip import GeoIP


# settings
custom_mappings = getattr(settings, 'GEOIP_LANGUAGES', {})
geoip_database = getattr(settings, 'GEOIP_DATABASE', '/usr/share/GeoIP/GeoIP.dat')
fallback_language = getattr(settings, 'GEOIP_FALLBACK_LANGUAGE', 'en')


class IPLocator(object):
    _database = GeoIP(geoip_database)
    _custom_mappings = custom_mappings
    _fallback_language = fallback_language

    def get_country(self, addr):
        return self._database.country_code_by_addr(addr)

    def get_language(self, addr):
        country = self.get_country(addr)
        return self._custom_mappings.get(country, self._fallback_language)


iplocator = IPLocator()

