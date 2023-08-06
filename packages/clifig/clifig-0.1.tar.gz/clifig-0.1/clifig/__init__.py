import cmd
import os
import ConfigParser


class Clifig(cmd.Cmd):
    @staticmethod
    def run(conf):
        Clifig(conf).cmdloop()

    def __init__(self, conf):
        cmd.Cmd.__init__(self)

        self.prompt = '('+os.path.basename(conf)+') '
        self.config = ConfigParser.ConfigParser()
        self.config.read(conf)
        self.config_file = conf

    def do_show(self, line):
        '''show [SECTION [OPTION]]'''
        options = line.split(' ')

        if len(options) <= 2:
            if len(options) is 2:
                try:
                    print(self.config.get(options[0], options[1]))
                except(ConfigParser.NoSectionError):
                    print('Section "'+options[0]+'" does not exist.')
                except(ConfigParser.NoOptionError):
                    print('Option "'+options[0]+'" does not exist.')
            elif options[0] is not '':
                try:
                    for (option, value) in self.config.items(options[0]):
                        print(option+':\t'+value)
                except(ConfigParser.NoSectionError):
                    print('Section "'+options[0]+'" does not exist.')
            else:
                for section in self.config.sections():
                    print('['+section+']')
                    for (option, value) in self.config.items(section):
                        print('\t'+option+':\t'+value)
        else:
            print(self.do_show.__doc__)

    def do_add(self, line):
        '''add SECTION'''
        options = line.split(' ')

        if options[0] is not '':
            try:
                self.config.add_section(options[0])
            except(ConfigParser.DuplicateSectionError):
                print('Section "'+options[0]+'" already exists.')
            except(ValueError):
                print('Invalid section name.')
        else:
            print(self.do_add.__doc__)

    def do_set(self, line):
        '''set SECTION OPTION VALUE'''
        options = line.split(' ')

        if len(options) is 3:
            try:
                self.config.set(options[0], options[1], options[2])
            except(ConfigParser.NoSectionError):
                print('Section "'+options[0]+'" does not exist.')
        else:
            print(self.do_set.__doc__)

    def do_del(self, line):
        '''del SECTION [OPTION]'''
        options = line.split(' ')

        if options[0] is not '' and len(options) <= 2:
            if len(options) is 2:
                try:
                    self.config.remove_option(options[0], options[1])
                except(ConfigParser.NoSectionError):
                    print('Section "'+options[0]+'" does not exist.')
                except(ConfigParser.NoOptionError):
                    print('Option "'+options[0]+'" does not exist.')
            else:
                try:
                    self.config.remove_section(options[0])
                except(ConfigParser.NoSectionError):
                    print('Section "'+options[0]+'" does not exist.')
        else:
            print(self.do_show.__doc__)

    def do_abort(self, line):
        '''Aborts changes and exits'''
        return True

    def do_exit(self, line):
        '''Saves the config to file and exits'''
        config_file_object = open(self.config_file, 'w')
        self.config.write(config_file_object)
        config_file_object.close()
        return True

    def do_EOF(self, line):
        '''Saves the config to file and exits'''
        config_file_object = open(self.config_file, 'w')
        self.config.write(config_file_object)
        config_file_object.close()
        return True
