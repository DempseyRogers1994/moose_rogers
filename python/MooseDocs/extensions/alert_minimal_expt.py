from ..base import components, LatexRenderer, HTMLRenderer, MarkdownReader
from ..tree import tokens, html, latex
from . import command, materialicon

def make_extension(**kwargs):
    return lertExtension(**kwargs)

AlertToken = tokens.newToken('AlertToken', brand='')
AlertTitle = tokens.newToken('AlertTitle', brand='', prefix=True, center=False, icon=True, icon_name=None)
AlertContent = tokens.newToken('AlertContent')

ALERT_LATEX = """ """

class lertExtension(command.CommandExtension):
    """
    Adds alert boxes (note, tip, error, warning, and construction) to display important information.
    """

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['use-title-prefix'] = (True, "Enable/disable including the brand (e.g., ERROR) as " \
                                            "prefix for the alert title.")
        return config

    def extend(self, reader, renderer):
        self.requires(command)
        self.addCommand(reader, MyCommand())
        renderer.add('AlertToken', RenderAlertToken())
        renderer.add('AlertTitle', RenderAlertTitle())
        renderer.add('AlertContent', RenderAlertContent())

        if isinstance(renderer, LatexRenderer):
            renderer.addPackage('xcolor')
            renderer.addPackage('xparse')
            renderer.addPackage('xifthen')
            renderer.addPackage('tcolorbox')
            renderer.addPackage('wrapfig')
            renderer.addPackage('graphicx')

            #renderer.addPreamble('\\definecolor{alert-construction}{RGB}{0,0,0}')
            renderer.addPreamble(ALERT_LATEX)

        if isinstance(renderer, HTMLRenderer):
            renderer.addCSS('alert_moose', "css/alert_moose.css")

class MyCommand(command.CommandComponent):
    COMMAND = 'alert'
    SUBCOMMAND = ( 'construction')
    

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['title'] = (None, "The optional alert title.")
        settings['center-title'] = (False, "Center the title.")
        settings['prefix'] = (None, "Enable/disable the title being prefixed with the alert brand.")
        settings['icon'] = (True, "Enable/disable the title icon.")
        settings['icon-name'] = (None, "Set the icon name, see material icon for available options.")
        return settings

    def createToken(self, parent, info, page, settings):
        title = settings.pop('title', None)
        brand = info['subcommand']
        icon_name = settings['icon-name']
        if icon_name is None:
            if brand == 'note':
                icon_name = 'comment'
            elif brand == 'construction':
                icon_name = 'comment'

        if settings['prefix'] is not None:
            prefix = settings['prefix']
        else:
            prefix = self.extension.get('use-title-prefix', True)

        alert_token = AlertToken(parent, brand=brand)
        title_token = AlertTitle(alert_token, prefix=prefix, brand=brand,
                                 icon=settings['icon'],
                                 icon_name=icon_name,
                                 center=settings['center-title'])

        return AlertContent(alert_token, brand=brand)

class RenderAlertToken(components.RenderComponent):

    def createMaterialize(self, parent, token, page):
        return html.Tag(parent, 'div',
                        class_='card moose-alert moose-alert-{}'.format(token['brand']))


class RenderAlertContent(components.RenderComponent):

    def createMaterialize(self, parent, token, page):

        card_content = html.Tag(parent, 'div', class_='card-content')
        content = html.Tag(card_content, 'div', class_='moose-alert-content')
        return content

class RenderAlertTitle(components.RenderComponent):

    def createMaterialize(self, parent, token, page):

        title = html.Tag(parent, 'div', class_='card-title moose-alert-title')
        if token.get('icon'):
            i = html.Tag(title, 'i', token, string=token['icon_name'])
            i.addClass('material-icons')
            i.addClass('moose-inline-icon')

        if token.get('prefix'):
            brand = token['brand']
            prefix = html.Tag(title, 'span', string=brand, class_='moose-alert-title-brand')
            if token.children:
                html.String(prefix, content=':')

        if token.get('center'):
            title.addClass('center')

        return title
