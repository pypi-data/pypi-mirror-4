from Products.ATContentTypes.content.topic import ATTopic
if hasattr(ATTopic.queryCatalog.im_func, '__doc__'):
    del ATTopic.queryCatalog.im_func.__doc__
