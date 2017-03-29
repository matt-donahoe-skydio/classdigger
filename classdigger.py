import os
import inspect
from jinja2 import Template
from dill.source import getsource


class ClassDigger(object):
    def __init__(self, cls):
        self.cls = cls
        self.structure = self.get_structure(cls)

    def get_file(self, member):
        '''
        Tells which file the method came from
        '''

        #TODO alternate approaches:
        # inspect.getmodule(object)
        # inspect.getsourcefile(object)
        try:
            f = inspect.getabsfile(member)
        except TypeError:
            f = None
        return f

    def get_user_attributes(self,cls):
        vanilla_object = dir(type('dummy', (object,), {}))
        return [item 
                for item in inspect.getmembers(cls)
                if item[0] not in vanilla_object
                ]

    def get_structure(self, cls):

        #Supers is all the super classes. First one on the list is this class itself. 
        supers = list(inspect.getmro(cls))
        supers.pop(0)
        structure = {'cls': cls, 'supers': supers, 'members': []}

        #Cycle through all methods and attributes of the class. 
        #.getmembers(cls) includes methods and attributes inherited from all parents.
        #.getmembers(cls) returns members in alphabetical order by name
        for name, member in self.get_user_attributes(cls):

            #Stores data about this method/attr while in the for loop. 
            #This will be appended to the class structure at end of loop.
            structure_member = {
                'obj': member,
                'name': name,
                'file': self.get_file(member)
                }

            #add the source code of the method
            try:
                #This will get the source line from whichever class 
                structure_member['lines'] = inspect.getsourcelines(member)
                structure_member['type'] = 'method'
                print('method of final class {}'.format(name))
                #print("-------------")
                #print(structure_member['lines'])

                print(getsource(member))

            #Attributes will return  a TypeError since they don't have getsourcelines method
            #TODO instead use inspect.ismethod(object) . maybe also useful, but not necessarly:inspect.getattr_static()
            except TypeError as e:
                structure_member['lines'] = [
                    ['    %s = %s\n' % (name, member)]]
                structure_member['type'] = 'attr'

            #For each super tracing up the heirarchy see if this method exists.
            # If the method exactly matches the method of the inspected class, the method has not been overwritten
            # Keep tracing, and each time a matching class is found higher up the tree, overwrite the current 'root' 
            # data. This means the last root found will persist. 
            for _super in supers:
                for _sname, _smember in inspect.getmembers(_super):
                    if self.is_excluded(_sname):
                        continue
                    if _sname == name:
                        print("found method named {} in {}".format(_sname,_super))
                    if _sname == name and _smember == member:
                        print("found duplicate method {} in {}".format(_sname,_super))

                        #Add context about the super
                        structure_member['root'] = {
                                'obj': _smember,
                                'cls': _super,
                                'file': self.get_file(_super)
                            }

                        print(structure_member['root']['file'])
            
            #TODO this is for debugging only
            #write out what we found about where this came from
            try:
                print("Final root file: {}".format(structure_member['root']['file']))
            except:
                pass


            #List all attr first, then all methods
            if structure_member['type'] == 'attr':
                structure['members'].insert(0, structure_member)
            else:
                structure['members'].append(structure_member)


        #Create a list of the inheritance structure
        inherited = list(map(lambda x: x.__name__, structure['supers']))
        print(inherited)
        if len(inherited) > 1:
            #Everything inherits from 'object', no need to include in list
            inherited.pop(inherited.index('object'))

        #Add a line to the top that displays all parent classes in form "class myClass(parent, grandparent):"
        structure['inherited'] = 'class %s(%s):\n' % (
            structure['cls'].__name__, ','.join(inherited))


        return structure

    def as_text(self):
        txt = self.structure['inherited']
        for member in self.structure['members']:
            lines = member['lines'][0][:]

            #TODO refactor this to use the root data no matter what - and original code should write 'root' when it finds first instance
            if member.get('root'):
                lines[0] = lines[0].replace(
                    '\n', '  # %s %s \n' % (
                        member['root']['file'],
                        member['root']['cls']))
            txt += '\n' + ''.join(lines)

        return txt

    def as_html(self):
        
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


if __name__ == '__main__':
    from examples.d import D
    from pprint import pprint
    parser = ClassDigger(D)
    #pprint(parser.structure)
    #print('\n\n')
    #print(parser.as_html())
    parser.write('examples/results.py', overwrite=True)
    parser.write('examples/results.html', overwrite=True,
                 contents=parser.as_html())
