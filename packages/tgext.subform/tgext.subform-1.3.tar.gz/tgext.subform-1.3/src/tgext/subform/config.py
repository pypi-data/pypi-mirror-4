from tgext.admin import AdminConfig
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.subform.controller import SubformController

class TgSubformAdminConfig(TGAdminConfig):
    DefaultControllerConfig=SubformController
    
class SubformAdminConfig(AdminConfig):
    DefaultControllerConfig=SubformController
