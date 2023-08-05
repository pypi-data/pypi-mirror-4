"""Python Vimeo API Wrapper."""

__version__ = '0.1.8'
__all__ = ['Client']

USER_AGENT = 'Vimeo Python API Wrapper %s' % __version__

from vimeo.client import Client
