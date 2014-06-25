__author__ = 'Christopher Bock'

from LoggingClass import LoggingClass


class OptionHandler(LoggingClass):
    """
    Option handler which is able to validate options as well as to parse arguments from the terminal as well as from a
    config file. Validators take as argument the value, they have to do the type checking themselves and have to return
    a boolean and print the error messages also themselves.
    By default only one validator per option may be supplied and trying to override it will result in an error!
    You can change this behaviour by setting the option 'allowReplaceValidator' to True
    """

    def __init__(self, logger):
        LoggingClass.__init__(self, logger)
        self.Options = {}
        self.validators = {}

        self.DefaultOptions = {
            'suppressValidtorWarnings': True,
            'suppressOptionWarnings': True,
            'allowReplaceValidator': False,
        }

        for key, value in self.DefaultOptions.iteritems():
            self.Options[key] = value

        self.load_defaults(self.DefaultOptions)

        self.shorthands = []
        self.long_names = {}
        self.mappings = {}
        self.help_texts = {}
        self.defaults = {}

        return

    def __getitem__(self, key):
        return self.get_option(key)

    def __setitem__(self, key, value):
        return self.set_option(key, value)

    def __iter__(self):
        return self.Options.itervalues()

    def iteritems(self):
        for key, value in self.Options.iteritems():
            yield (key, value)

    def add_terminal_argument(self, shorthand, long_name, help_text, maps_to, default):
        if shorthand in self.shorthands:
            self.print_log('Option %s is already being parsed!', 'ERROR')
            return

        if long_name in self.long_names.keys():
            self.print_log('The long name of option %s, %s, is already used!', 'ERROR')
            return

        self.shorthands.append(shorthand)
        self.long_names[shorthand] = long_name
        self.help_texts[shorthand] = help_text
        self.mappings[shorthand] = maps_to
        self.defaults[shorthand] = default

        return

    def parse_arguments_terminal(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', help='Path to the config file to use.')
        parser.add_argument('-d', '--debug', help='Enable debug mode!')

        for shorthand in self.shorthands:
            parser.add_argument(shorthand, self.long_names[shorthand], help=self.help_texts[shorthand],
                                default=self.defaults[shorthand])

        args = parser.parse_args()
        if args.debug:
            self.set_option('debug', True)

        for shorthand in self.shorthands:
            self.print_log('Mapping: %s to %s' % (shorthand, self.long_names[shorthand].replace('--', '')))
            self.Options[self.mappings[shorthand]] = eval('args.%s' % self.long_names[shorthand].replace('--', ''))

        # this has to be the last config option to be checked!!
        if args.config:
            return self.parse_arguments_config_file(args.config)

        return True

    def parse_arguments_config_file(self, path_config_file='default.cfg'):
        self.print_log('Parsing configuration file %s' % path_config_file, 'INFO')
        import os

        if not os.path.exists(path_config_file):
            self.print_log('Config file does not exist! Aborting!', 'ERROR')
            return False

        cfgFile = open(path_config_file)
        if not cfgFile:
            print('An unknown error occured while opening the config file: %s' % path_config_file)
        else:
            for line in cfgFile.readlines():
                line = line.strip()
                if line == '' or line.startswith('#'):
                    continue
                line = line.split(';')
                if len(line) > 2:
                    if not self.parse_option_from_cfg_file(line):
                        self.print_log('Unable to parse option %s from config file %s.' % (str(line), path_config_file),
                                      'ERROR')
                        self.print_log('Options have to be specified in the following manner: ', 'ERROR')
                        self.print_log('Name of the option;option value;option type', 'ERROR')
                        self.print_log(
                            'The value and the type are optional. If no type is specified a string is assumed.',
                            'ERROR')
                        self.print_log('If value and type have not been specified, the option will be set to True.',
                                      'ERROR')
                        self.print_log('Only specifying the type and the name will not work!', 'ERROR')
                        self.print_log('Lines starting with: # will be ignored by the option parser.', 'ERROR')
                        return False
                elif len(line) == 2:
                    self.set_option(line[0].strip(), line[1].strip())
                elif len(line) == 1:
                    self.set_option(line[0].strip(), True)
        return True

    def parse_option_from_cfg_file(self, option_array):
        if not option_array:
            self.print_log('Tried to parse an option from a config file without specifing an option array!', 'ERROR')
            return False

        if len(option_array) < 3:
            self.print_log('When calling parse_option_from_cfg_file the option array is expected to have three entries!',
                          'ERROR')
            return False

        option_type = option_array[2].strip().lower()
        option_value = option_array[1].strip()
        value = eval('%s(option_value)' % option_type)

        self.set_option(option_array[0].strip(), value)

        return True

    def set_option(self, key, value, validator=None):
        """
        If 'suppressOptionWarnings' is set to False, a warning message will be printed if an option is being overridden.
        'suppressOptionWarnings' defaults to True.
        """
        if validator:
            if not self.set_validator(key, validator):
                self.print_log(
                    'Could not set the option %s because the validator you supplied, %s, caused a problem!' % (
                    str(key), str(validator)), 'ERROR')
                return False

        if key in self.validators.keys():
            if not self.validators[key](value):
                self.print_log('Could not verify option %s, with value %s against validator %s!' % (
                               str(key), str(value), str(validator)), 'ERROR')
                return False

        if not self.get_option('suppressOptionWarnings'):
            if key in self.Options.keys():
                self.print_log('You are overriding option %s. Replacing value %s by %s.' % (
                               str(key), str(self.Options[key]), str(value)), 'WARNING')

        self.Options[key] = value
        setattr(self, key, value)

        return True

    def set_validator(self, key, validator):
        if key in self.validators.keys():
            if not self.get_option('allowReplaceValidator'):
                self.print_log('A validator for %s is already in place! You tried to override %s with %s.' % (
                str(key), str(self.validators[key]), str(validator)), 'ERROR')
                return False
            else:
                self.print_log('You are overriding the validator for %s! Overreding %s with %s.' % (
                str(key), str(self.validators[key]), str(validator)), 'WARNING')

        self.validators[key] = validator
        return True

    def load_defaults(self, defaultOptions, defaultValidators=None, overrideByDefaults=False):
        """
        defaultOptions has to be a dictionary of key -> value pairs for the options to be specified, the same for defaultValidators
        the defaultValidators will be parsed first if specified. The dictionaries do not have to be in the same order, neither do they
        have to be of equal length
        """
        keepOptions = not overrideByDefaults
        if defaultValidators:
            for key, validator in defaultValidators.iteritems():
                if not (self.has_validator(key) and keepOptions):
                    self.set_validator(key, validator)

        for key, value in defaultOptions.iteritems():
            if not (self.has_option(key) and keepOptions):
                self.set_option(key, value)

        return

    def get_option(self, key):
        if not key in self.Options.keys():
            self.print_log('Tried to access an option (%s) which has not yet been specified!' % key, 'WARNING')
            return None
        return self.Options[key]

    def has_option(self, key):
        return key in self.Options.keys()

    def has_validator(self, key):
        return key in self.validators.keys()

    def validate_all_options(self):
        """
        this will validate all options, if the option 'suppressValidtorWarnings' is False (defaults to True),
        a list of all options without a validator will be printed
        returns True if all options for which validators have been supplied are valid
        """
        optionsWithoutValidator = []
        notValidOptions = []

        for key in self.Options.keys():
            if key in self.validators.keys():
                if not self.validators[key](self.Options[key]):
                    notValidOptions.append(key)
            else:
                optionsWithoutValidator.append(key)

        if not self.get_option('suppressValidtorWarnings'):
            msg_type = 'WARNING'
            self.print_line(msg_type)
            self.print_log("  The following validators are missing:  ", msg_type)

            for key in optionsWithoutValidator:
                self.print_log('     %s' % str(key), msg_type)

            self.print_log("  End of missing validator list ", msg_type)
            self.print_line(msg_type)

        msg_type = 'ERROR'
        self.print_line(msg_type)
        self.print_log("  The following options are invalid:  ", msg_type)

        for key in notValidOptions:
            self.print_log('     %s' % str(key), msg_type)

        self.print_log("  End of invalid option list ", msg_type)
        self.print_line(msg_type)

        return len(notValidOptions) <= 0

    def print_options(self, msg_type='DEBUG'):
        self.print_line(msg_type)
        self.print_log("  The following options have been supplied  ", msg_type)

        for key, value in self.Options.iteritems():
            self.print_log('    ' + str(key) + '  ->  ' + str(value), msg_type)

        self.print_log("  End of option listing  ")
        self.print_line(msg_type)
        return

    def print_validators(self, msg_type='DEBUG'):
        self.print_line(msg_type)
        self.print_log("  The following validators have been supplied  ", msg_type)

        for key, validator in self.validators.iteritems():
            self.print_log('    ' + str(key) + '  ->  ' + str(validator), msg_type)

        self.print_log("  End of validator listing  ")
        self.print_line(msg_type)
        return
