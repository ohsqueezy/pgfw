from os import walk, remove
from os.path import sep, join, exists, normpath
from re import findall

from configuration.Configuration import *

class Setup:

    config = Configuration()

    @classmethod
    def remove_old_mainfest(self):
        path = "MANIFEST"
        if exists(path):
            remove(path)

    @classmethod
    def build_package_list(self):
        packages = []
        package_root = self.config.get("setup", "package-root")
        if exists(package_root):
            for root, dirs, files in walk(package_root, followlinks=True):
                packages.append(root.replace(sep, "."))
        return packages

    @classmethod
    def build_data_installation_map(self):
        include = []
        config = self.config.get_section("setup")
        install_root = config["installation-path"]
        exclude = map(normpath, config["data-exclude"])
        print exclude
        for root, dirs, files in walk("."):
            dirs = self.remove_excluded_dirs(dirs, root, exclude)
            for file_name in files:
                path = normpath(join(root, file_name))
                if path not in exclude:
                    include.append((normpath(join(config["installation-path"],
                                                  root)), path))
        return include

    @classmethod
    def remove_excluded_dirs(self, dirs, root, exclude):
        removal = []
        for directory in dirs:
            if normpath(join(root, directory)) in exclude:
                removal.append(directory)
        for directory in removal:
            dirs.remove(directory)
        return dirs

    @classmethod
    def translate_title(self):
        return self.config["game-title"].replace(" ", "-")

    @classmethod
    def build_description(self):
        return "\n%s\n%s\n%s" % (file("description").read(),
                                 "Changelog\n=========",
                                 self.translate_changelog())

    @classmethod
    def translate_changelog(self):
        translation = ""
        for line in file("changelog"):
            line = line.strip()
            if line.startswith("esp-hadouken"):
                version = findall("\((.*)\)", line)[0]
                translation += "\n%s\n%s\n" % (version, "-" * len(version))
            elif line and not line.startswith("--"):
                if line.startswith("*"):
                    translation += line + "\n"
                else:
                    translation += "  " + line + "\n"
        return translation
