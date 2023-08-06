from pydna.download import Genbank as _Genbank
import sys
import os
import percache
cache = percache.Cache("/tmp/genbank-cache")

def _get_proxy_from_global_settings():

    """Get proxy settings."""
    if sys.platform.startswith('linux'):
        try:
            from gi.repository import Gio
        except ImportError:
            return
        mode = Gio.Settings.new('org.gnome.system.proxy').get_string('mode')
        if mode == 'none':
            return ''
        http_settings = Gio.Settings.new('org.gnome.system.proxy.http')
        host = http_settings.get_string('host')
        port = http_settings.get_int('port')
        if http_settings.get_boolean('use-authentication'):
            username = http_settings.get_string('authentication_user')
            password = http_settings.get_string('authentication_password')
        else:
            username = password = None
            return 'http://{}:{}'.format(host,port)

_proxy = _get_proxy_from_global_settings()

_gbloader = _Genbank("bjornjobb@gmail.com",_proxy)

@cache
def gb(item):
    return _gbloader.nucleotide(item)


