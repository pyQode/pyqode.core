"""
This package contains some pygments styles plugins unique to pyqode:
    - qt: a light color scheme inspired by the default Qt creator color scheme
    - darcula: a dark color scheme inspired by the IntelliJ Idea's darcula
               theme

"""
from pygments.style import Style
from pygments.token import Comment, Error, Generic, Keyword, Literal, Name, \
     Operator, Text, Token, String, String


class QtStyle(Style):
    """
    Port of the qt style
    """
    default_style = ''

    background_color = '#ffffff'

    styles = {
        Comment.Multiline: 'italic #008000',
        Comment.Preproc: '#000080',
        Comment.Single: 'italic #008000',
        Comment.Special: 'bold italic #000080',
        Comment: 'italic #008000',
        Error: '#CC0000',
        Generic.Deleted: 'bg:#ffdddd #000000',
        Generic.Emph: 'italic #000000',
        Generic.Error: '#aa0000',
        Generic.Heading: '#999999',
        Generic.Inserted: 'bg:#ddffdd #000000',
        Generic.Output: '#888888',
        Generic.Prompt: '#555555',
        Generic.Strong: 'bold',
        Generic.Subheading: '#aaaaaa',
        Generic.Traceback: '#aa0000',
        Keyword.Constant: '#808000 ',
        Keyword.Declaration: '#808000',
        Keyword.Namespace: '#808000',
        Keyword.Pseudo: '#808000',
        Keyword.Reserved: '#808000',
        Keyword.Type: '#800080',
        Keyword: '#808000',
        Literal.Number: '#000080',
        Literal.String: '#000080',
        Name.Attribute: '#800080',
        Name.Builtin.Pseudo: '#AA00AA',
        Name.Builtin: '#AA00AA',
        Name.Class: '#800080',
        Name.Constant: '#000000',
        Name.Decorator: '#808000',
        Name.Entity: '#000000',
        Name.Exception: '#800080',
        Name.Function: '#800000',
        Name.Label: '#800000',
        Name.Namespace: '#000000',
        Name.Tag: '#0000FE',
        Name.Variable.Class: '#800080',
        Name.Variable.Global: '#000000',
        Name.Variable.Instance: '#800000',
        Name.Variable: '#000000',
        Operator.Word: '#000000',
        Operator: '#000000',
        Text.Whitespace: '#BFBFBF',
    }

#
class DarculaStyle(Style):
    """
    Pygments color scheme inspired by the darcula theme (Pycharm/IntelliJ Idea)

    """
    background_color = '#252525'

    styles = {
        Comment.Multiline: 'italic #808080',
        Comment.Preproc: '#808080',
        Comment.Single: 'italic #808080',
        Comment.Special: 'bold italic #808080',
        Comment: 'italic #808080',
        Error: '#CC0000',
        Generic.Deleted: 'bg:#ffdddd #A9B7C6',
        Generic.Emph: 'italic #A9B7C6',
        Generic.Error: '#aa0000',
        Generic.Heading: '#999999',
        Generic.Inserted: 'bg:#ddffdd #A9B7C6',
        Generic.Output: '#888888',
        Generic.Prompt: '#555555',
        Generic.Strong: 'bold',
        Generic.Subheading: '#aaaaaa',
        Generic.Traceback: '#aa0000',
        Keyword.Constant: '#CC7832 ',
        Keyword.Declaration: '#CC7832',
        Keyword.Namespace: '#CC7832',
        Keyword.Pseudo: '#CC7832',
        Keyword.Reserved: '#CC7832',
        Keyword.Type: '#A9B7C6 bold',
        Keyword: '#CC7832',
        Literal.Number: '#6897B3',
        Literal.String: '#629755 italic',
        Literal.String.Doc: '#A5C261 italic',
        Name.Attribute: '#800080',
        Name.Builtin.Pseudo: '#cc7832',
        Name.Builtin: '#cc7832',
        Name.Class: '#A9B7C6 bold',
        Name.Constant: '#A9B7C6 bold',
        Name.Decorator: '#BBB529 bold',
        Name.Entity: '#A9B7C6',
        Name.Exception: '#A9B7C6 bold',
        Name.Function: '#A9B7C6 bold',
        Name.Label: '#A9B7C6 bold',
        Name.Namespace: '#A9B7C6',
        Name.Tag: '#0000FE',
        Name.Variable.Class: '#A9B7C6 bold',
        Name.Variable.Global: '#A9B7C6 bold',
        Name.Variable.Instance: '#A9B7C6',
        Name.Variable: '#A9B7C6',
        Operator.Word: '#A9B7C6',
        Operator: '#A9B7C6',
        Text: '#A9B7C6',
        Text.Whitespace: '#2a2a2a',
    }