def includeme(config):
    config.include('.static_files')
    config.include('.front')
    config.include('.account')
    config.include('.admin', route_prefix='/admin')