from lemon.config import ConfigBase


class Config(ConfigBase):
    urls = {
        'name': 'index',
        'controller': 'lemon.controllers.simple.SimpleController',
        'renders': { 'html': 'lemon.renders.Jinja2Render' },
    }
