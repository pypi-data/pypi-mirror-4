def pyclass2enum(enumname, value):
    enumvalues = []
    for name, value in value.__dict__.items():
        if name.startswith('__'):
            continue
        if not isinstance(value, int): # enum values are supposed to be int
            continue
        enumvalues.append('    {}{}={}'.format(enumname, name, value))
    if enumvalues:
        return 'typedef enum {{\n{}\n}} {};'.format(',\n'.join(enumvalues), enumname)
    else:
        return ''
    
def py2objc(name, value):
    if isinstance(value, type):
        # It's a class, which is supposed to represent an enum.
        return pyclass2enum(name, value)
    if isinstance(value, (int, float)):
        value = str(value)
    elif isinstance(value, str):
        value = '@"{}"'.format(value)
    else:
        raise TypeError("Value {} of type {} unsupported.".format(repr(value), type(value)))
    return "#define {} {}".format(name, value)

def generate_objc_code(module, dest):
    consts = []
    for name, value in module.__dict__.items():
        if name.startswith('__'):
            continue
        consts.append(py2objc(name, value))
    contents = '\n\n'.join(consts)
    with open(dest, 'wt', encoding='utf-8') as fp:
        fp.write(contents)
