__version__ = '0.1'
__description__ = 'Microdata semantic markups support for Pelican Blog Generator'

def register():
    from microdata import plugin
    plugin.register()
