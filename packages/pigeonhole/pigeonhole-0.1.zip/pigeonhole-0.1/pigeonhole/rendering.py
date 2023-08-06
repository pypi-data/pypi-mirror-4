from zope.pagetemplate.pagetemplate import PageTemplate

CONFIGS = {}


def post_render(config):
    """
    Keep the configuration after rendering
    """
    CONFIGS[config.template_dir] = config


def pagetemplate_renderer(template, context):
    pt = PageTemplate()
    pt.write(template)
    return pt.pt_render(context)
