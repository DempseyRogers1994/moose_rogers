# Writing an extension from scratch
import os
import pandas as pd
from ..base import components, LatexRenderer, HTMLRenderer, MarkdownReader
from ..tree import tokens, html, latex
from ..common import __init__ 
from . import command, materialicon

# This method prints to the command line as expected
#data=[[1,2,3],[1,2,3],[1,2,3]]
#df=pd.DataFrame(columns=['a','b','c'],data=data)
#print(df)

def make_extension(**kwargs):  #reqired extension
    return GreetingExtension(**kwargs)




GreetingToken = tokens.newToken('GreetingToken', brand='')
GreetingTitle = tokens.newToken('GreetingTitle', brand='', prefix=True, center=False, icon=True, icon_name=None)
GreetingContent = tokens.newToken('GreetingContent')


GREETING_LATEX="""\\setlength\\intextsep{0pt}
\\NewDocumentEnvironment{alert}{O{#2}moO{white}}{%
  \\ifthenelse{\\isempty{#1}}{%
      \\IfValueT{#3}{\\tcbset{title=#3}}
    }{%
      \\tcbset{title=\\MakeUppercase{#1}\\IfValueT{#3}{: #3}}
    }
  \\begin{tcolorbox}[arc=0mm,fonttitle=\\bfseries,colback=alert-#2!5,colframe=alert-#2,coltitle=#4]
}{%
  \\end{tcolorbox}
}
"""

class GreetingExtension(command.CommandExtension):
    def extend(self, reader, renderer):
        self.requires(command)
        self.addCommand(reader, GreetingCommand())
        renderer.add('GreetingToken', RenderGreetingToken())
        renderer.add('GreetingTitle', RenderGreetingTitle())
        renderer.add('GreetingContent', RenderGreetingContent())


        if isinstance(renderer, LatexRenderer):
            renderer.addPackage('xcolor')
            renderer.addPackage('xparse')
            renderer.addPackage('xifthen')
            renderer.addPackage('tcolorbox')
            renderer.addPackage('wrapfig')
            renderer.addPackage('graphicx')

            renderer.addPreamble('\\definecolor{greeting-english}{RGB}{153,0,0}')
            renderer.addPreamble('\\definecolor{greeting-spanish}{RGB}{0,88,151}')

            renderer.addPreamble(GREETING_LATEX)

        if isinstance(renderer, HTMLRenderer):
            renderer.addCSS('greeting_moose', "css/greeting_moose.css")



class GreetingCommand(command.CommandComponent):
    COMMAND= 'mygreeting'
    SUBCOMMAND= ('english' ,'spanish', 'french')

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['title'] = (None, "The optional greeting title.")
        settings['center-title'] = (False, "Center the title.")
        settings['prefix'] = (None, "Enable/disable the title being prefixed with the greeting brand.")
        settings['icon'] = (True, "Enable/disable the title icon.")
        settings['icon-name'] = (None, "Set the icon name, see material icon for available options.")
        return settings


    def createToken(self, parent, info, page, settings):
        brand = info['subcommand']
        icon_name = settings['icon-name']

        if brand =='english':
            title=' hello world'
            icon_name='comment'
        elif brand == 'french':
            title = ' bonjour le monde'
            icon_name= 'report'
        else:
            title=' hola mundo'
            icon_name= 'school'
        
        if settings['prefix'] is not None:
            prefix = settings['prefix']
        else:
            prefix = self.extension.get('use-title-prefix', True)

        greeting_token = GreetingToken(parent, brand=brand) #generates the card and its text, must be on
        title_token = GreetingTitle(greeting_token, prefix=prefix, brand=brand,
                                 icon=settings['icon'],
                                 icon_name=icon_name,
                                 center=settings['center-title'])

        if title:
            self.reader.tokenize(title_token, title, page, MarkdownReader.INLINE)

        return GreetingContent(greeting_token, brand=brand)

class RenderGreetingToken(components.RenderComponent):

#___________________________________________________________________________
    def createHTML(self, parent, token, page):
        return(html.Tag(parent, 'div', class_='moose-greeting moose-greeting-{}'.format(token['brand'])))
    
#___________________________________________________________________________

    def createMaterialize(self, parent, token, page):
        return html.Tag(parent, 'div', class_='moose-greeting moose-greeting-{}'.format(token['brand']))

#___________________________________________________________________________
    def createLatex(self, parent, token, page):

        # Argument list (see GREETING above)
        args = []
        if token(0)['prefix']:
            args.append(latex.Bracket(string=token['brand']))
        else:
            args.append(latex.Bracket())

        args.append(latex.Brace(string=token['brand']))

        if token(0).children:
            title = latex.Bracket()
            self.renderer.render(title, token(0), page)
            args.append(title)

        env = latex.Environment(parent, 'greeting', args=args)

        token(0).parent = None
        return env
#___________________________________________________________________________

class RenderGreetingContent(components.RenderComponent):
    def createHTML(self, parent, token, page):
        return html.Tag(parent, 'div',  class_='moose-greeting-content')
#___________________________________________________________________________
    def createMaterialize(self, parent, token, page):
        card_content = html.Tag(parent, 'div', class_='card-content')
        content = html.Tag(card_content, 'div', class_='moose-greeting-content')
        return content

    def createLatex(self, parent, token,page):
        return parent
#___________________________________________________________________________
    

class RenderGreetingTitle(components.RenderComponent):
    def createHTML(self, parent, token, page):
        if token.get('icon'):
            i= html.Tag(parent, 'div', class_='moose-greeting-title')
            i.addClass('material-icons')
            i.addClass('moose-inline-icon')

            if token.get('prefix'):
                brand = token['brand']
                prefix = html.Tag(title, 'span', string=brand, class_='moose-greeting-title-brand')
                if token.children:
                    html.String(prefix, content=': ')

        return title

    def createMaterialize(self, parent, token, page):
        title = html.Tag(parent, 'div',  class_='card-title moose-gretting-title')
        if token.get('icon'):
            i = html.Tag(title, 'i', token, string=token['icon_name'])
            i.addClass('material-icons')
            i.addClass('moose-inline-icon')

        if token.get('prefix'):
            brand = token['brand']
            prefix = html.Tag(title, 'span', string=brand, class_='moose-greeting-title-brand')
            if token.children:
                html.String(prefix, content=':')


        if token.get('center'):
            title.addClass('center')
        return title

