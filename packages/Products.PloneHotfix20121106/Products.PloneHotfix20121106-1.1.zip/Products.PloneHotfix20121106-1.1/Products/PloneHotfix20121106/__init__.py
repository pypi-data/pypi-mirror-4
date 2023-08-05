import logging
logger = logging.getLogger('Products.PloneHotfix20121106')

hotfixes = [
    'registerConfiglet',
    'setHeader',
    'allow_module',
    'get_request_var_or_attr',
    'kssdevel',
    'widget_traversal',
    'gtbn',
    'kupu_spellcheck',
    'membership_tool',
    'queryCatalog',
    'uid_catalog',
    'renameObjectsByPaths',
    'at_download',
    'safe_html',
    'python_scripts',
    'getNavigationRootObject',
    'crypto_oracle',
    'crypto_oracle_p3',
    'crypto_oracle_protect',
    'ftp',
    'atat',
    'random_string',
    ]

# figure out which hotfixes to apply
try:
    import kss.core
except ImportError:
    hotfixes.remove('kssdevel')

try:
    import Products.kupu.python
except ImportError:
    hotfixes.remove('kupu_spellcheck')

try:
    import plone.z3cform
except ImportError:
    hotfixes.remove('widget_traversal')

try:
    from plone.app.layout.navigation.root import getNavigationRootObject
except ImportError:
    hotfixes.remove('getNavigationRootObject')

try:
    from plone.session import tktauth
except ImportError:
    hotfixes.remove('crypto_oracle')

try:
    import plone.session.sources.hash
except ImportError:
    hotfixes.remove('crypto_oracle_p3')

try:
    import plone.protect
except ImportError:
    hotfixes.remove('crypto_oracle_protect')

# Apply the fixes
for hotfix in hotfixes:
    try:
        __import__('Products.PloneHotfix20121106.%s' % hotfix)
        logger.info('Applied %s patch' % hotfix)
    except:
        logger.warn('Could not apply %s' % hotfix)
logger.info('Hotfix installed')
