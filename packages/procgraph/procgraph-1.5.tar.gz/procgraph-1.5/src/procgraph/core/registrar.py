

class Library:

    def __init__(self, parent=None):
        self.parent = parent

        self.name2block = {}

        # Set of filenames already looked into
        self.loaded_files = set()

    def exists(self, block_type):
        if block_type in self.name2block:
            return True
        else:
            if self.parent is not None:
                return self.parent.exists(block_type)
            else:
                return False

    def register(self, block_type, generator):
        if  self.exists(block_type):
            raise ValueError('Type %r already registered.' % block_type)

        self.name2block[block_type] = generator

    def instance(self, block_type, name, config, library=None):
        if library is None:
            library = self
        generator = self.get_generator_for_block_type(block_type)
        block = generator(name=name, config=config, library=library)
        return block

    def get_generator_for_block_type(self, block_type):
        ''' Returns the generator object for the block type.
        
            A generator can instance using:
            
                generator(name, config, library)
                
            and it can provide (before instancing) the properties:
            
                generator.config
                generator.input
                generator.output
        '''

        if not self.exists(block_type):
            msg = 'Block %r does not exist.' % block_type
            raise ValueError(msg)

        if block_type in self.name2block:
            generator = self.name2block[block_type]
            return generator
        else:
            assert self.parent
            return self.parent.get_generator_for_block_type(block_type)

    def get_known_blocks(self):
        blocks = list(self.name2block.keys())
        if self.parent:
            blocks.extend(self.parent.get_known_blocks())
        return blocks


default_library = Library()



