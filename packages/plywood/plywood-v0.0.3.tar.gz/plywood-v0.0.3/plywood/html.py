

def html(buffer, attributes, content, block):
    buffer.append('<html' + attributes() + '>')
    if block:
        buffer.append('\n')
        buffer.append(block())
        buffer.append('\n')
    buffer.append('</html>')
