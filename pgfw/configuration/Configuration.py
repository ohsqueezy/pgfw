from os import sep, getcwd
from os.path import join, exists, basename, dirname
from sys import argv
from pprint import pformat

from ConfigParser import RawConfigParser

class Configuration(RawConfigParser):

    default_rel_path = "config"
    defaults_file_path = "defaults"

    def __init__(self, installed_resources_path=None, rel_path=None,
                 type_declarations=None, local=False):
        RawConfigParser.__init__(self)
        self.local = local
        self.set_type_declarations(type_declarations)
        self.installed_resources_path = installed_resources_path
        self.rel_path = rel_path
        self.read_defaults()
        self.read_project_file()
        if self.is_debug_mode():
            print self

    def set_type_declarations(self, type_declarations):
        if type_declarations is None:
            type_declarations = TypeDeclarations()
        self.type_declarations = type_declarations

    def set(self, section, option, value):
        value = self.cast_value(section, option, value)
        RawConfigParser.set(self, section, option, value)

    def cast_value(self, section, option, value):
        pair = section, option
        types = self.type_declarations
        if type(value) == str:
            if pair in types["bool"]:
                return True if value == "yes" else False
            elif pair in types["int"]:
                return int(value)
            elif pair in types["float"]:
                return float(value)
            elif pair in types["path"]:
                return join(*value.split(sep))
            elif pair in types["list"]:
                return map(str.strip, value.split(types.list_member_sep))
            elif pair in types["int-list"]:
                return map(int, value.split(types.list_member_sep))
        return value

    def read_defaults(self):
        self.read(join(dirname(__file__), self.defaults_file_path))
        self.set("setup", "package-root", basename(getcwd()))

    def read(self, filenames):
        files_read = RawConfigParser.read(self, filenames)
        for section in self.sections():
            for option, value in self.items(section):
                self.set(section, option, value)
        return files_read

    def read_project_file(self):
        path = self.locate_project_file()
        if path:
            self.read(path)
        elif self.is_debug_mode():
            print "No configuration file found"

    def is_debug_mode(self):
        return "-d" in argv

    def locate_project_file(self):
        rel_path = self.rel_path if self.rel_path else self.default_rel_path
        if not self.is_local_mode():
            installed_path = join(self.installed_resources_path, rel_path)
            if exists(installed_path):
                return installed_path
        if exists(rel_path):
            return rel_path

    def is_local_mode(self):
        return "-l" in argv or self.local

    def get(self, section, option):
        value = RawConfigParser.get(self, section, option)
        if value is None:
            value = self.get_substitute(section, option)
        return value

    def get_substitute(self, section, option):
        if section == "display":
            if option == "caption":
                return self.get("setup", "title")

    def get_section(self, section):
        assignments = {}
        for option in self.options(section):
            assignments[option] = self.get(section, option)
        return assignments

    def __repr__(self):
        config = {}
        for section in self.sections():
            config[section] = self.get_section(section)
        return pformat(config, 2, 1)


class TypeDeclarations(dict):

    list_member_sep = ','

    def __init__(self):
        dict.__init__(self, {"bool": [], "int": [], "float": [], "path": [],
                             "list": [], "int-list": []})
        self.add("int", "display", "frame-duration")
        self.add("int", "display", "wait-duration")
        self.add("bool", "display", "centered")
        self.add("int-list", "display", "dimensions")
        self.add("path", "resources", "installation-path")
        self.add("path", "screen-captures", "path")
        self.add("list", "setup", "classifiers")
        self.add("list", "keys", "up")
        self.add("list", "keys", "right")
        self.add("list", "keys", "down")
        self.add("list", "keys", "left")

    def add(self, type, section, option):
        self[type].append((section, option))
