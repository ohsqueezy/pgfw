from os import walk, remove
from os.path import sep, join, exists, normpath
from re import findall

from configuration.Configuration import *

class Setup:

    config = Configuration()

    def remove_old_mainfest(self):
        path = "MANIFEST"
        if exists(path):
            remove(path)

    def build_package_list(self):
        packages = []
        package_root = self.config.get("setup", "package-root")
        if exists(package_root):
            for root, dirs, files in walk(package_root, followlinks=True):
                packages.append(root.replace(sep, "."))
        return packages

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

    def remove_excluded_dirs(self, dirs, root, exclude):
        removal = []
        for directory in dirs:
            if normpath(join(root, directory)) in exclude:
                removal.append(directory)
        for directory in removal:
            dirs.remove(directory)
        return dirs

    def translate_title(self):
        return self.config.get("setup", "title").replace(" ", "-")

    def build_description(self):
        return "\n%s\n%s\n%s" % (file("description").read(),
                                 "Changelog\n=========",
                                 self.translate_changelog())

    def translate_changelog(self):
        translation = ""
        path = self.config.get("setup", "changelog")
        if exists(path):
            lines = file(path).readlines()
            package_name = lines[0].split()[0]
            for line in lines:
                line = line.strip()
                if line.startswith(package_name):
                    version = findall("\((.*)\)", line)[0]
                    translation += "\n%s\n%s\n" % (version, "-" * len(version))
                elif line and not line.startswith("--"):
                    if line.startswith("*"):
                        translation += line + "\n"
                    else:
                        translation += "  " + line + "\n"
        return translation
