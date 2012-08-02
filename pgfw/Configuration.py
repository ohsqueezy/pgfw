from os import sep, getcwd
from os.path import join, exists, basename, dirname, expanduser
from sys import argv
from pprint import pformat

from ConfigParser import RawConfigParser

class Configuration(RawConfigParser):

    default_project_file_rel_path = "config"
    default_resources_paths = [".", "resources"]

    def __init__(self, project_file_rel_path=None, resources_path=None,
                 type_declarations=None):
        RawConfigParser.__init__(self)
        self.project_file_rel_path = project_file_rel_path
        self.resources_path = resources_path
        self.set_type_declarations(type_declarations)
        self.set_defaults()
        self.read_project_config_file()
        self.modify_defaults()
        self.print_debug(self)

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
                return self.translate_path(value)
            elif pair in types["list"]:
                if value == "":
                    return []
                else:
                    return map(str.strip, value.split(types.list_member_sep))
            elif pair in types["int-list"]:
                return map(int, value.split(types.list_member_sep))
        return value

    def translate_path(self, path):
        new = ""
        if path and path[0] == sep:
            new += sep
        return expanduser("{0}{1}".format(new, join(*path.split(sep))))

    def set_defaults(self):
        add_section = self.add_section
        set_option = self.set
        section = "setup"
        add_section(section)
        set_option(section, "package-root", basename(getcwd()))
        set_option(section, "title", "") 
        set_option(section, "classifiers", "")
        set_option(section, "resources-search-path", "./, resources/")
        set_option(section, "installation-dir", "/usr/local/share/games/")
        set_option(section, "changelog", "changelog")
        set_option(section, "description-file", "")
        set_option(section, "init-script", "") 
        set_option(section, "version", "")
        set_option(section, "summary", "")
        set_option(section, "license", "")
        set_option(section, "platforms", "")
        set_option(section, "contact-name", "")
        set_option(section, "contact-email", "")
        set_option(section, "url", "")
        set_option(section, "requirements", "")
        set_option(section, "main-object", "pgfw/Game.py")
        set_option(section, "resources-path-identifier", "resources_path")
        set_option(section, "special-char-placeholder", "_")
        set_option(section, "whitespace-placeholder", "-")
        section = "display"
        add_section(section)
        set_option(section, "dimensions", "480, 320")
        set_option(section, "frame-duration", "33")
        set_option(section, "wait-duration", "2")
        set_option(section, "caption", "") 
        set_option(section, "centered", "yes")
        section = "screen-captures"
        add_section(section)
        set_option(section, "rel-path", "caps")
        set_option(section, "file-name-format", "%Y-%m-%d_%H:%M:%S")
        set_option(section, "file-extension", "png")
        section = "keys"
        add_section(section)
        set_option(section, "up", "K_UP, K_w")
        set_option(section, "right", "K_RIGHT, K_d")
        set_option(section, "down", "K_DOWN, K_s")
        set_option(section, "left", "K_LEFT, K_a")
        set_option(section, "capture-screen", "K_F9")
        section = "event"
        add_section(section)
        set_option(section, "custom-event-id", "USEREVENT")
        set_option(section, "command-event-name", "command")

    def read(self, filenames):
        files_read = RawConfigParser.read(self, filenames)
        for section in self.sections():
            for option, value in self.items(section):
                self.set(section, option, value)
        return files_read

    def read_project_config_file(self):
        path = self.locate_project_config_file()
        if path:
            self.read(path)
        else:
            self.print_debug("No configuration file found")

    def locate_project_config_file(self):
        rel_path = self.project_file_rel_path
        if not rel_path:
            rel_path = self.default_project_file_rel_path
        if exists(rel_path) and not self.is_shared_mode():
            return rel_path
        if self.resources_path:
            installed_path = join(self.resources_path, rel_path)
            if exists(installed_path):
                return installed_path

    def is_shared_mode(self):
        return "-s" in argv

    def print_debug(self, statement):
        if self.is_debug_mode():
            print statement
            
    def is_debug_mode(self):
        return "-d" in argv

    def modify_defaults(self):
        self.set_installation_path()
        self.set_resources_search_path()
        self.set_screen_captures_path()
        self.set_data_exclusion_list()
        self.set_requirements()

    def set_installation_path(self):
        self.set("setup", "installation-path",
                 join(self.get("setup", "installation-dir"),
                      self.get("setup", "package-root")))

    def set_resources_search_path(self):
        section, option = "setup", "resources-search-path"
        search_path = self.get(section, option)
        if self.resources_path:
            search_path.append(self.resources_path)
        else:
            search_path.append(self.get("setup", "installation-path"))
        self.set(section, option, search_path)

    def get(self, section, option):
        value = RawConfigParser.get(self, section, option)
        if value is None:
            value = self.get_substitute(section, option)
        return value

    def get_substitute(self, section, option):
        if section == "display":
            if option == "caption":
                return self.get("setup", "title")

    def set_screen_captures_path(self):
        section, option = "screen-captures", "path"
        if not self.has_option(section, option):
            self.set(section, option, join(self.build_home_path(),
                                           self.get(section, "rel-path")))

    def build_home_path(self):
        return join("~", "." + self.get("setup", "package-root"))

    def set_data_exclusion_list(self):
        section, option = "setup", "data-exclude"
        exclude = []
        if self.has_option(section, option):
            exclude = self.get(section, option)
        exclude += [".git", ".gitignore", "README", "build/", "dist/",
                    "setup.py", "MANIFEST", "PKG-INFO",
                    self.get("setup", "package-root"),
                    self.get("setup", "changelog")]
        self.set(section, option, exclude)

    def set_requirements(self):
        section, option = "setup", "requirements"
        requirements = []
        if self.has_option(section, option):
            requirements = self.get(section, option)
        if "pygame" not in requirements:
            requirements.append("pygame")
        self.set(section, option, requirements)

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
    defaults = {"display": {"int": ["frame-duration", "wait-duration"],
                            "bool": "centered",
                            "int-list": "dimensions"},
                "screen-captures": {"path": "path"},
                "setup": {"list": ["classifiers", "resources-search-path",
                                   "requirements", "data-exclude"],
                          "path": ["installation-dir", "package-root",
                                    "changelog", "description-file",
                                    "main-object"]},
                "keys": {"list": ["up", "right", "down", "left"]}}
    additional_defaults = {}

    def __init__(self):
        dict.__init__(self, {"bool": [], "int": [], "float": [], "path": [],
                             "list": [], "int-list": []})
        self.add_chart(self.defaults)
        self.add_chart(self.additional_defaults)

    def add(self, cast, section, option):
        self[cast].append((section, option))

    def add_chart(self, chart):
        for section, declarations in chart.iteritems():
            for cast, options in declarations.iteritems():
                if type(options) != list:
                    options = [options]
                for option in options:
                    self.add(cast, section, option)
