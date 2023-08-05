from middleware import SCSSMiddleware

def plugme(app_config, options):
    def mount_scss_middleware(app):
        return SCSSMiddleware(app)
    app_config.register_hook('after_config', mount_scss_middleware)
    return dict(appid='tgext.scss')
