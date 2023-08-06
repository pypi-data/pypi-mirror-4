import os
import re
import ConfigParser

CONFIG_PATH = os.path.expanduser('~/.staticgallery/config.cfg')
config = ConfigParser.ConfigParser()

if os.path.exists(CONFIG_PATH):
    config.read(CONFIG_PATH)

SUPPORTED_IMAGES = ('image/jpeg', 'image/png', 'image/gif')
SRC_GALLERY_PATH = config.get('staticgallery', 'SRC_GALLERY_PATH')

if SRC_GALLERY_PATH.startswith('~'):
    SRC_GALLERY_PATH = os.path.expanduser(SRC_GALLERY_PATH)

DST_GALLERY_PATH = config.get('staticgallery', 'DST_GALLERY_PATH')

if DST_GALLERY_PATH.startswith('~'):
    DST_GALLERY_PATH = os.path.expanduser(DST_GALLERY_PATH)

TEMPLATES_PATH = config.get('staticgallery', 'TEMPLATES_PATH')
THUMBS_NAME = config.get('staticgallery', 'THUMBS_NAME')
INDEX_HTML = config.get('staticgallery', 'INDEX_HTML')
THUMBS_SIZE = config.get('staticgallery', 'THUMBS_SIZE')
GALLERY_TPL = config.get('staticgallery', 'GALLERY_TPL')
MENU_TPL = config.get('staticgallery', 'MENU_TPL')

THUMBS_SIZE = tuple(int(num) for num in re.findall('[0-9]+', THUMBS_SIZE))
