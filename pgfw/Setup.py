from os import walk, remove
from os.path import sep, join, exists, normpath
from re import findall, sub
from distutils.core import setup
from distutils.command.install import install
from pprint import pprint
from fileinput import FileInput
from re import sub, match

from Configuration import *

class Setup:

    config = Configuration()
    manifest_path = "MANIFEST"

    def remove_old_mainfest(self):
        path = self.manifest_path
        if exists(path):
            remove(path)

    def build_package_list(self):
        packages = []
        package_root = self.config.get("setup", "package-root")
        if exists(package_root):
            for root, dirs, files in walk(package_root, followlinks=True):
                packages.append(root.replace(sep, "."))
        return packages

    def build_data_map(self):
        include = []
        config = self.config.get_section("setup")
        exclude = map(normpath, config["data-exclude"])
        for root, dirs, files in walk("."):
            dirs = self.remove_excluded(dirs, root, exclude)
            files = [join(root, f) for f in self.remove_excluded(files, root,
                                                                 exclude)]
            if files:
                include.append((normpath(join(config["installation-path"],
                                              root)), files))
        return include

    def remove_excluded(self, paths, root, exclude):
        removal = []
        for path in paths:
            if normpath(join(root, path)) in exclude:
                removal.append(path)
        for path in removal:
            paths.remove(path)
        return paths

    def translate_title(self):
        config = self.config.get_section("setup")
        title = config["title"].replace(" ", config["whitespace-placeholder"])
        return sub("[^\w-]", config["special-char-placeholder"], title)

    def build_description(self):
        description = ""
        path = self.config.get("setup", "description-file")
        if exists(path):
            description = "\n{0}\n{1}\n{2}".format(file(path).read(),
                                                   "Changelog\n=========",
                                                   self.translate_changelog())
        return description

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

    def setup(self):
        self.remove_old_mainfest()
        config = self.config.get_section("setup")
        setup(cmdclass={"install": insert_resources_path},
              name=self.translate_title(),
              packages=self.build_package_list(),
              scripts=[config["init-script"]],
              data_files=self.build_data_map(),
              requires=config["requirements"],
              version=config["version"],
              description=config["summary"],
              classifiers=config["classifiers"],
              long_description=self.build_description(),
              license=config["license"],
              platforms=config["platforms"],
              author=config["contact-name"],
              author_email=config["contact-email"],
              url=config["url"])


class insert_resources_path(install):

    def run(self):
        install.run(self)
        self.edit_game_object_file()

    def edit_game_object_file(self):
        config = Configuration().get_section("setup")
        for path in self.get_outputs():
            if path.endswith(config["main-object"]):
                for line in FileInput(path, inplace=True):
                    pattern = "^ *{0} *=.*".\
                              format(config["resources-path-identifier"])
                    if match(pattern, line):
                        line = sub("=.*$", "= \"{0}\"".\
                                   format(config["installation-path"]), line)
                    print line.strip("\n")
