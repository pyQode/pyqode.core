from pygments.style import Style
from pygments.token import Comment, Error, Generic, Keyword, Literal, Name, \
    Operator, Text, Punctuation


class DarculaStyle(Style):
    """
    Pygments color scheme inspired by the darcula theme (Pycharm/IntelliJ Idea)

    """
    background_color = '#252525'
    highlight_color = '#353535'

    styles = {
        Comment.Multiline: ' #808080',
        Comment.Preproc: '#808080',
        Comment.Single: ' #808080',
        Comment.Special: 'bold  #808080',
        Comment: ' #808080',
        Error: '#CC0000',
        Generic.Deleted: 'bg:#ffdddd #A9B7C6',
        Generic.Emph: ' #A9B7C6',
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
        Literal.String: '#629755 ',
        Literal.String.Doc: '#A5C261 ',
        Name.Attribute: '#800080',
        Name.Builtin.Pseudo: '#94558D',
        Name.Builtin: '#cc7832',
        Name.Class: '#A9B7C6 bold',
        Name.Constant: '#A9B7C6 bold',
        Name.Decorator: '#BBB529',
        Name.Entity: '#A9B7C6',
        Name.Exception: '#A9B7C6 bold',
        Name.Function: '#A9B7C6 bold',
        Name.Label: '#A9B7C6 bold',
        Name.Namespace: '#A9B7C6',
        Name.Tag: '#A5C261 bold',
        Name.Variable.Class: '#A9B7C6 bold',
        Name.Variable.Global: '#A9B7C6 bold',
        Name.Variable.Instance: '#A9B7C6',
        Name.Variable: '#A9B7C6',
        Operator.Word: '#A9B7C6',
        Operator: '#A9B7C6',
        Text: '#A9B7C6',
        Text.Whitespace: '#2a2a2a',
        Punctuation: '#A9B7C6'
    }
