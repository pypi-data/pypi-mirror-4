def includeme(config):
    config.add_route('front.home', '/')
    config.add_route('front.set_lang', '/set_lang/{lang}')