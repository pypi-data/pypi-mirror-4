# player public api

__all__ = ['tmpl_filter', 'wrap_layout', 'add_message',
           'render', 'RendererNotFound', 'includeme']

from player.layer import tmpl_filter
from player.layout import wrap_layout
from player.renderer import render
from player.renderer import RendererNotFound
from player.message import add_message


def includeme(cfg):
    import os
    from pyramid.path import AssetResolver
    from pyramid.settings import aslist
    from pyramid.exceptions import ConfigurationError

    from player.renderer import lt_renderer_factory
    from player.layer import add_layer, add_layers, change_layers_order
    from player.layer import add_tmpl_filter
    from player.layout import add_layout, set_layout_data

    # config directives
    cfg.add_directive('add_layer', add_layer)
    cfg.add_directive('add_layers', add_layers)
    cfg.add_directive('add_layout', add_layout)
    cfg.add_directive('add_tmpl_filter', add_tmpl_filter)

    # request.render_tmpl
    cfg.add_request_method(render, 'render_tmpl')

    # request.set_layout_data
    cfg.add_request_method(set_layout_data, 'set_layout_data')

    # renderer factory
    cfg.add_renderer('.lt', lt_renderer_factory)

    # order
    settings = cfg.get_settings()

    order = {}
    for key, val in settings.items():
        if key.startswith('layer.order.'):
            layer = key[12:]
            order[layer] = [s.strip() for s in aslist(val)]

    if order:
        cfg.action(
            'player.order',
            change_layers_order, (cfg, order), order=999999+1)

    # global custom layer
    custom = settings.get('layer.custom', '').strip()
    if custom:
        resolver = AssetResolver()
        directory = resolver.resolve(custom).abspath()
        if not os.path.isdir(directory):
            raise ConfigurationError(
                "Directory is required for layer.custom setting: %s"%custom)

        cfg.action(
            'player.custom',
            add_layers, (cfg, 'layer_custom', custom), order=999999+2)

    # formatters
    from player import formatter
    cfg.add_directive('add_formatter', formatter.add_formatter)
    cfg.add_request_method(formatter.formatters, 'fmt', True, True)

    # messages layer and request helpers
    from player.message import render_messages

    cfg.add_layer('message', path='player:templates/message/')

    cfg.add_request_method(add_message, 'add_message')
    cfg.add_request_method(render_messages, 'render_messages')

    # scan
    cfg.scan('player')
