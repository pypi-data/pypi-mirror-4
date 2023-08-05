from Products.CMFCore import utils as CMFCoreUtils

def initialize(context):
    import MockMailHost
    tools = (MockMailHost.MockMailHost, )
    CMFCoreUtils.ToolInit(MockMailHost.META_TYPE,
                          tools=tools,
                          icon='MailHost_icon.gif').initialize(context)
