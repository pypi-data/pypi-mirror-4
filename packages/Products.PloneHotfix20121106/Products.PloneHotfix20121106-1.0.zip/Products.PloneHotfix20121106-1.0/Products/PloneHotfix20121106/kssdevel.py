from kss.core.pluginregistry.browser.develview import DevelView
if hasattr(DevelView, 'publishTraverse'):
    DevelView.__bobo_traverse__ = DevelView.publishTraverse
    del DevelView.publishTraverse
