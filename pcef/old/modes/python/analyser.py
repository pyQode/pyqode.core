import weakref


class DocumentNodeType:
    ROOT = 0
    FUNCTION = 1
    CLASS = 2
    IMPORTS = 3

    @classmethod
    def toString(cls, t):
        if t == cls.ROOT:
            return "ROOT"
        elif t == cls.FUNCTION:
            return "FUNCTION"
        elif t == cls.CLASS:
            return "CLASS"
        else:
            return "IMPORTS"


class DocumentNode(object):
    def __init__(self, identifier, node_type=DocumentNodeType.ROOT):
        self.identifier = identifier
        self.start = None
        self.end = None
        self.type = node_type
        self.indentation_level = 0
        self.children = []
        self.__parent = None

    @property
    def parent(self):
        return self.__parent()

    def add_child(self, child):
        child.__parent = weakref.ref(self)
        self.children.append(child)

    def finalize(self, lines):
        """
        Close nodes
        """
        starts = []
        for c in self.children:
            starts.append(c.start)
        starts.append(self.end)
        for i in range(len(starts) - 1):
            self.children[i].end = starts[i + 1] - 1
        for c in self.children:
            c.finalize(lines)
        ch = []
        for c in self.children:
            finish = False
            while not finish:
                l = lines[c.end - 1].strip()
                if c.identifier == "on_actionOpen_triggered":
                    pass
                empty_line = l.isspace() or l == "" or "@" in l
                if c.end <= 0 or not empty_line:
                    finish = True
                else:
                    c.end -= 1
            ch.append(c)
        self.children[:] = ch


    def debug_print(self, indent=0):
        print " " * indent, self.identifier, self.start, self.end, \
            self.indentation_level, DocumentNodeType.toString(self.type)
        for c in self.children:
            c.debug_print(indent + 4)


def get_line_indentation_level(line):
    return len(line) - len(line.lstrip())


def parse(source_code):
    lines = source_code.splitlines()
    imports = DocumentNode("Imports", DocumentNodeType.IMPORTS)
    root = DocumentNode("Root")
    root.start = 1
    root.end = len(lines) + 1
    root.add_child(imports)
    last_node = root
    prev_indent_level = 0
    for i, line in enumerate(lines):
        indent_lvl = get_line_indentation_level(line)
        # imports
        if line.strip().startswith('import') or \
                line.strip().startswith("from"):
            if not imports.start:
                imports.start = i + 1
            imports.end = i + 1
        if line.strip().startswith("def") or line.strip().startswith("class"):
            node_type = DocumentNodeType.CLASS
            if line.strip().startswith("def"):
                node_type = DocumentNodeType.FUNCTION
            try:
                n = DocumentNode(line.lstrip().split(" ")[1].split("(")[0],
                                 node_type)
                n.indentation_level = indent_lvl
                n.start = i + 1
                if indent_lvl < prev_indent_level:
                    last_node = last_node.parent
                    if not last_node:
                        last_node = root
                    last_node.add_child(n)
                elif indent_lvl > prev_indent_level:
                    last_node = last_node.children[len(last_node.children)-1]
                    last_node.add_child(n)
                else:
                    last_node.add_child(n)
                prev_indent_level = indent_lvl
            except IndexError:
                pass
    root.finalize(lines)
    return root