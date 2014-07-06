from pygments.style import Style
from pygments.token import Comment, Error, Generic, Keyword, Literal, Name, \
    Operator, Text


class QtStyle(Style):
    """
    Port of the qt style
    """
    default_style = ''

    background_color = '#ffffff'
    highlight_color = '#eeeeee'

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
        Literal.String.Doc: '#8080FF italic',
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
        Text: '#000000',
        Text.Whitespace: '#BFBFBF',
    }