
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack #@UnusedImport

from flask_metaroute.func import attach_controllers
import importlib
    
class MetaRoute(object):
    
    def __init__(self, app = None, ctrl_pkg = None):
        if app is not None:
            self.app = app
            self.init_app(self.app, ctrl_pkg)
        else:
            self.app = None

    def init_app(self, app, ctrl_pkg = None):
        pkg = ctrl_pkg or app.config['METAROUTE_CONTROLLERS_PKG']
        if isinstance(pkg, str):
            pkg = importlib.import_module(pkg)
            
        
        attach_controllers(app, pkg)
