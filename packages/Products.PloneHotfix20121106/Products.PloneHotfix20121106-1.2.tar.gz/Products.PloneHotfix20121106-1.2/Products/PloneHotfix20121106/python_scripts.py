from Shared.DC.Scripts.Bindings import Bindings
from zExceptions import NotFound


DO_NOT_PUBLISH = [
    'getFolderContents',
    'selectedTabs',
    'pwreset_constructURL',
    'createMultiColumnList',
    'create_query_string',
    'formatColumns',
    'getPopupScript',
    'getObjectsFromPathList',
    'translate',
    'utranslate',
    'queryCatalog'
    ]

_original_bindAndExec = Bindings._bindAndExec
def _patched_bindAndExec(self, args, kw, caller_namespace):
    '''
    Prepares the bound information and calls _exec(),
    possibly with a namespace.
    '''
    if hasattr(self, 'getId'):
        id = self.getId()
        if (id in DO_NOT_PUBLISH and
                self.REQUEST.get('PUBLISHED') is self):
            raise NotFound('Script may not be published.')

        if id == 'createObject':
            try:
                arg = args[0]
                if arg is not None:
                    args = list(args)
                    args[0] = arg.replace('$', '$$')
                    args = tuple(args)
            except IndexError:
                pass
            try:
                arg = kw['id']
                if arg is not None:
                    kw['id'] = arg.replace('$', '$$')
            except KeyError:
                pass

        if id == 'go_back':
            try:
                arg = args[0]
                if arg is not None:
                    args = list(args)
                    args[0] = arg.replace('$', '$$')
                    args = tuple(args)
            except IndexError:
                pass
            try:
                arg = kw['last_referer']
                if arg is not None:
                    kw['last_referer'] = arg.replace('$', '$$')
            except KeyError:
                pass
    
    return _original_bindAndExec(self, args, kw, caller_namespace)
Bindings._bindAndExec = _patched_bindAndExec
