from collections import defaultdict
import inspect
import os
import re

"""
ancestors = cls.mro()[1:]
member_list = []
member
for ancestor in ancestors:
    name = ancestor.__name__
    for member in getmembers(ancestor):
        member_list.append((name, member.__name__, member))


Then iterate over the top class

for member in get_members(cls):
    latest = None
    owner = None
    for ancestor in reversed(ancestors):
        if this ancestor changed the value
            anc_value = getattr(ancestor, member.__name__)
            if anc_value != latest:
                print('changed')
                latest = anc_value
                owner = ancestor
            write("__{ancestor}__{member}  = {value}")
            latest = ancestor
        write("{member} = __{latest}__{member}")

Oh shit, does the mro change? Do we need to re-do it for each ancestor when they call super??
Make a test

Methods are harder. We need to track the supers().
That way we can see what it is, where it came from, and can easily change the value.

    super(cls, self).method(args, **kwargs)

Becomes:

    def __R3__method(args, **kwargs):
        pass

    def method(args, **kwargs):
        self.__R3__method(args, **kwargs)



We can assert that the super matches a regex
"""

def create_unique_name(cls, name):
    return f"__{cls.__name__}__{name}"


PY2_SUPER_PATTERN = re.compile("(.*)super\((.*), self\)\.(.*)")

def member_history(cls, output_parent_classes=tuple()):
    lines = []
    newname = f"{cls.__name__}Flat"

    # Go through all the objects
    ancestors = cls.mro()
    # TODO(matt): support a base_cls input to the function, and don't include those methods in the output

    if not output_parent_classes:
        parents = ["object"]
    else:
        parents = [p.__name__ for p in output_parent_classes]

    classes_to_ignore = set()
    for parent in output_parent_classes:
        for ancestor in parent.mro():
            classes_to_ignore.add(ancestor)


    lines.append(f"class {newname}({', '.join(p for p in parents)}):\n")
    # Then iterate over members of just the top class
    for member_type in ('attr', 'method'):
        for name, member in inspect.getmembers(cls):
            if name.startswith('__'):
                continue
            try:
                inspect.getsourcelines(member)
                if member_type == 'attr':
                    continue
            except:
                if member_type == 'method':
                    continue
                # we are either attr or property
                if isinstance(member, property):
                    continue
            latest = None
            previous = None
            set_any = False
            owner = None  # wtf was this?
            for ancestor in reversed(ancestors):
                # if this ancestor changed the value
                try:
                    anc_value = getattr(ancestor, name)
                except AttributeError:
                    continue
                if latest is None or anc_value != latest:
                    if latest is not None and set_any:
                        print(f"{name} changed from {latest} to {anc_value} in {ancestor.__name__}")
                    set_any = False
                    latest = anc_value
                    previous = owner
                    owner = ancestor
                    unique_name = create_unique_name(ancestor, name)
                    if owner in classes_to_ignore:
                        pass
                    elif member_type == 'method':
                        codelines, num = inspect.getsourcelines(anc_value)
                        lines.append("")
                        lines.append(f"    def {unique_name}(self):")
                        for line in codelines[1:]:
                            line = line.rstrip()
                            m = PY2_SUPER_PATTERN.search(line)
                            if m:
                                super_cls_arg = m.group(2)
                                assert super_cls_arg == ancestor.__name__

                                # TOOD(matt): don't assume indention
                                lines.append("        # Super call")

                                # remove the super() function and determine the correct member manually.
                                line = m.group(1) + f"self.__{previous.__name__}__" + m.group(3)
                                lines.append(line)

                                # Add a blank line
                                lines.append("")
                            else:
                                lines.append(line)
                        # TODO(matt): get the args
                    elif member_type == 'attr':
                        lines.append(f"    {unique_name} = {repr(anc_value)}")
                    elif member_type == 'property':
                        # TODO(matt): implmenet
                        continue
                    else:
                        raise TypeError(member_type)

            # then assign the non-unique name to the latest value.
            if latest is not None:
                if owner in classes_to_ignore:
                    continue
                elif member_type == 'attr':
                    lines.append(f"    {name} = __{owner.__name__}__{name}\n")
                else:
                    lines.append("")
                    lines.append(f"    def {name}(self):")
                    lines.append(f"        return self.{create_unique_name(owner, name)}()")
    return '\n'.join(lines)


class ClassDigger(object):
    def __init__(self, cls):
        self.cls = cls
        self.structure = self.get_structure(cls)

    def is_excluded(self, name):
        return name.startswith('__')

    def get_file(self, member):
        try:
            f = inspect.getabsfile(member)
        except TypeError:
            f = None
        return f

    def get_structure(self, cls):
        supers = list(inspect.getmro(cls))
        supers.pop(0)  # get rid of cls from the list
        structure = {'cls': cls, 'supers': supers, 'members': []}
        for name, member in inspect.getmembers(cls):
            if self.is_excluded(name):
                continue
            structure_member = {
                'obj': member,
                'name': name,
                'file': self.get_file(member)}
            is_method = None
            try:
                structure_member['lines'] = inspect.getsourcelines(
                    member)
                structure_member['type'] = 'method'
                is_method = True
            except:
                is_method = False
                structure_member['lines'] = [
                    ['    %s = %s\n' % (name, member)]]
                structure_member['type'] = 'attr'
            # TODO(matt): reverse this.
            for _super in reversed(supers):
                for _sname, _smember in inspect.getmembers(_super):
                    if self.is_excluded(_sname):
                        continue
                    # if the name matches, and the member is the same object, then this method has not been overridden:
                    if _sname == name:
                        if _smember == member:
                            # this is going to overwrite???
                            if 'root' in structure_member:
                                # we already did this one
                                pass
                            else:
                                structure_member['root'] = {
                                    'obj': _smember,
                                    'cls': _super,
                                    'file': self.get_file(_super)}
                        elif is_method:
                            print("method {} defined in {} but changed in {}".format(name, _super.__name__,  cls.__name__))
                        else:
                            print("attr {} was overridden from {} to {} by super {}".format(name, _smember, member, _super))

            # what is special about attributes?
            if structure_member['type'] == 'attr':
                structure['members'].insert(0, structure_member)
            else:
                structure['members'].append(structure_member)

        # why does this make them inherited?
        inherited = [x.__name__ for x in structure['supers']]
        if len(inherited) > 1:
            inherited.pop(inherited.index('object'))

        structure['inherited'] = 'class %s(%s):\n' % (
            structure['cls'].__name__, ','.join(inherited))
        return structure

    def as_text(self):
        txt = self.structure['inherited']
        for member in self.structure['members']:
            lines = member['lines'][0][:]
            if member.get('root'):
                lines[0] = lines[0].replace(
                    '\n', '  # %s %s \n' % (
                        member['root']['file'],
                        member['root']['cls']))
            txt += '\n' + ''.join(lines)

        return txt

    def as_html(self):
        from jinja2 import Template
        template = Template(open('template.html', 'r').read())
        return template.render(structure=self.structure)

    def write(self, path, overwrite=False, contents=None):
        if not overwrite and os.path.exists(path):
            raise IOError('File exists!')
        with open(path, 'w') as f:
            if not contents:
                f.write(self.as_text())
            else:
                f.write(contents)

def old_main():
    from examples.d import D
    from pprint import pprint
    parser = ClassDigger(D)
    pprint(parser.structure)
    print('\n\n')
    print(parser.as_html())
    parser.write('examples/results.py', overwrite=True)
    parser.write('examples/results.html', overwrite=True,
                 contents=parser.as_html())

def new_main():
    from examples.d import D
    import examples.a
    import examples.c
    output = member_history(D, output_parent_classes=[examples.a.Base2, examples.c.Mixin])

    # Manually add the imports, since classdigger does support that yet.
    print("from examples.a import Base2")
    print("from examples.c import Mixin")
    print("")
    print("")

    # Add the flattened class definition
    print(output)

if __name__ == '__main__':
    new_main()
