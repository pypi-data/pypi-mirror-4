import re

HEADER_FOOTER_REX = re.compile(
    r"^(\|[\-+]+\|)$"
    )

def is_separator(line):
    m = HEADER_FOOTER_REX.match(line.rstrip())
    if m is None:
        return 0
    return len(m.group(1))


def is_body(line, size):
    line = line.rstrip()
    try:
        return line[0] == "|" and line[size-1] == "|"
    except IndexError:
        return False



class LineSack(list):
    def rewrite(self):
        return self


class TableSack(list):
    def rewrite(self):

        skip_next = False
        
        for i in xrange(len(self)):
            if skip_next:
                skip_next = False
                continue
            line = self[i]
            if is_separator(line):
                try:
                    if is_separator(self[i+1]):
                        yield "+" + line[1:-1].replace("-", "=") + "+"
                        skip_next = True
                except IndexError:
                    pass
                # we didn't yield this separator already, so do it now
                if not skip_next:
                    yield "+" + line[1:-1] + "+"
            else:
                yield line
                


def group_input(lines):
    in_table = False

    accu = LineSack()
    separator_length = -1
    
    for line in lines:
        if not in_table:
            separator_length = is_separator(line)
            if not separator_length:
                accu.append(line)
            else:
                in_table = True
                yield accu
                accu = TableSack()
                accu.append(line)
        else:
            if is_body(line, separator_length):
                accu.append(line)
            else:
                yield accu
                separator_length = -1
                in_table = False
                accu = LineSack()
                accu.append(line)
    yield accu


def rewrite(text):
    lines = text.split("\n")
    outlines = []
    for group in group_input(lines):
        outlines.extend(group.rewrite())
    return "\n".join(outlines)
    

def source_read(app, docname, text):
    text[0] = rewrite(text[0])

    
def setup(app):
    app.connect("source-read", source_read)
    
