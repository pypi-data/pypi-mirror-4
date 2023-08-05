def remove_breaks(string):
    while string.find('\n') >= 0:
        string = string.replace('\n', '')
    return string


def remove_extra_space(string):
    while string.find('  ') >= 0:
        string = string.replace('  ', ' ')
    return string

def remove_extra_breaks(string):
    lines = string.split('\n')
    new_lines = []
    for line in lines:
        line = line.strip()
        if line != "":
            new_lines.append(line)
    return "\n".join(new_lines)
