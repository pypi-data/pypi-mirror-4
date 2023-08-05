from middleware import BrowserVersionMiddleware

def plugme(app_config, options):
    def add_middleware(app):
        return BrowserVersionMiddleware(app)
    app_config.register_hook('after_config', add_middleware)

    return dict(appid='tgext.browserlimit')