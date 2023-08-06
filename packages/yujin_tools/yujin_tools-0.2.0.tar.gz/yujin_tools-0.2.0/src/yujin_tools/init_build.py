##############################################################################
# Imports
##############################################################################

import os.path

import sys
import stat  # file permissions
import argparse
from argparse import RawTextHelpFormatter
import shutil

##############################################################################
# Local imports
##############################################################################

import console
import common

##############################################################################
# Methods
##############################################################################


def help_string():
    overview = 'This is a convenience script for auto-generating a catkin parallel build directory.\n\n'
    instructions = " \
 'yujin_init_build' prepares conventional ros build directories in ./ linked to sources in ./src \n \
 'yujin_init_build --release release' prepares a release directory in ./release linked to sources in ./src \n \
 'yujin_init_build debug ~/ecl/src' prepares a build directory in ./debug linked to sources in ~/ecl/src \n \
 'yujin_init_build --toolchain=arm-pc-linux-gnueabi arm' prepares a build directory in ./arm with the specified toolchain module \n \
"
    return overview + instructions


def parse_arguments():
    parser = argparse.ArgumentParser(description=help_string(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('dir', nargs='?', default="./", help='directory to use for the parallel development space [./]')
    parser.add_argument('sources', nargs='?', default="src", help='directory where the sources reside [./src]')
    parser.add_argument('-r', '--release', action='store_true', help='build in Release mode instead of RelWithDebugSymbols [false]')
    parser.add_argument('-i', '--install', action='store', default='/not_set_directory', help='installation location [workspace/install]')
    parser.add_argument('-u', '--underlays', action='store', default='/opt/ros/groovy', help='semi-colon list of catkin workspaces to utilise [/opt/ros/groovy]')
    parser.add_argument('-t', '--toolchain', action='store', default='', help='toolchain cmake module to load []')
    parser.add_argument('-p', '--platform', action='store', default='', help='platform cmake cache module to load []')
    parser.add_argument('--list-toolchains', action='store_true', help='list all currently available toolchain modules [false]')
    parser.add_argument('--list-platforms', action='store_true', help='list all currently available platform modules [false]')
    parser.add_argument('--track', action='store', default=None, help='retrieve rosinstalls relevant to this track [groovy|hydro][groovy]')
    parser.add_argument('--get-default-track', action='store_true', help='print the default track that is being followed to screen')
    parser.add_argument('--set-default-track', action='store', default=None, help='set a new default track to work from %s' % common.VALID_TRACKS)
    args = parser.parse_args()
    return args


def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, unused_fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def read_template(tmplf):
    f = open(tmplf, 'r')
    try:
        t = f.read()
    finally:
        f.close()
    return t


def fill_in_template(template, name, cwd):
    return template % locals()


def instantiate_template(filename, name, cwd):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'init_build')
    tmpl = read_template(os.path.join(template_dir, filename))
    contents = fill_in_template(tmpl, name, cwd)
    try:
        f = open(os.path.join(cwd, filename), 'w')
        f.write(contents.encode('utf-8'))
    finally:
        os.fchmod(f.fileno(), stat.S_IRWXU)
        f.close()


def fill_in_makefile(template, rel_source_dir, catkin_make, catkin_python_path, toolchain, override):
    return template % locals()


def instantiate_makefile(filename, build_dir, rel_source_dir, catkin_make, catkin_python_path, toolchain):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'init_build')
    tmpl = read_template(os.path.join(template_dir, filename))
    contents = fill_in_makefile(tmpl, rel_source_dir, catkin_make, catkin_python_path, toolchain, common.override_filename())
    try:
        f = open(os.path.join(build_dir, filename), 'w')
        f.write(contents.encode('utf-8'))
    finally:
        f.close()


def fill_in_config_cmake(template, config_install_prefix, config_underlays):
    return template % locals()


def instantiate_config_cmake(build_path, config_install_prefix, config_underlays):
    '''
      Copy the cache configuration template to the build path.
    '''
    template_dir = os.path.join(os.path.dirname(__file__), 'cmake')
    template = read_template(os.path.join(template_dir, "config.cmake"))
    contents = fill_in_config_cmake(template, config_install_prefix, config_underlays)
    config_cmake_file = os.path.join(build_path, "config.cmake")
    try:
        f = open(config_cmake_file, 'w')
        f.write(contents.encode('utf-8'))
    finally:
        f.close()


def print_build_details(build_dir, source_dir, install_prefix, build_type, underlays, name, toolchain, platform):
    console.pretty_println("*********** Parallel Development Workspace Details ***********", console.bold)
    console.pretty_print("Build directory : ", console.cyan)
    console.pretty_println(build_dir, console.yellow)
    console.pretty_print("Source directory: ", console.cyan)
    console.pretty_println(source_dir, console.yellow)
    console.pretty_print("Install prefix  : ", console.cyan)
    console.pretty_println(install_prefix, console.yellow)
    console.pretty_print("Build Type      : ", console.cyan)
    console.pretty_println(build_type, console.yellow)
    console.pretty_print("Underlays       : ", console.cyan)
    console.pretty_println(underlays, console.yellow)
    console.pretty_print("Eclipse Name    : ", console.cyan)
    console.pretty_println(name, console.yellow)
    if not toolchain == "":
        console.pretty_print("Toolchain       : ", console.cyan)
        console.pretty_println(toolchain, console.yellow)
    if not platform == "":
        console.pretty_print("Platform        : ", console.cyan)
        console.pretty_println(platform, console.yellow)
    console.pretty_println("**************************************************************", console.bold)


def list_toolchains():
    console.pretty_println("********************** Toolchain List ************************", console.bold)
    for (unused_dirpath, unused_dirname, filenames) in os.walk(os.path.join(os.path.dirname(__file__), 'toolchains')):
        for filename in filenames:
            print(" -- %s" % os.path.splitext(os.path.basename(filename))[0])
    console.pretty_println("**************************************************************", console.bold)


def list_platforms():
    console.pretty_println("*********************** Platform List ************************", console.bold)
    for (unused_dirpath, unused_dirname, filenames) in os.walk(os.path.join(os.path.dirname(__file__), 'platforms')):
        for filename in filenames:
            print(" -- %s" % os.path.splitext(os.path.basename(filename))[0])
    console.pretty_println("**************************************************************", console.bold)


def init_configured_build(build_dir_="./", source_dir_="./src", underlays_="/opt/ros/groovy", install_prefix_="./install", release_=False, toolchain_="", platform_=""):
    '''
      This one is used with pre-configured parameters. Note that
      init_build generates parameters parsed from the command line and then
      calls this function.
    '''
    # Help us build the name for the eclipse workspace...usually we call in the workspace itself.
    workspace_dir = os.getcwd()

    ##########################
    # Build directory
    ##########################
    if os.path.isabs(build_dir_):
        build_dir = build_dir_
    else:
        if build_dir_ == "." or build_dir_ == "./":
            build_dir = os.getcwd()
        else:
            build_dir = os.path.join(os.getcwd(), build_dir_)
    if not os.path.isfile(os.path.join(build_dir, "Makefile")):
        if not os.path.isdir(build_dir):  # remember ./ is a valid build dir, even if it's not populated yet
            os.mkdir(build_dir)
    else:
        console.logerror("This build directory is already initialised")
        sys.exit(1)

    ##########################
    # Source directory
    ##########################
    # Absolute path - should probably use os.path.abspath here
    #if os.path.isabs(source_dir_):
    #    source_dir = source_dir_
    #else:
    #    source_dir = os.path.join(os.getcwd(), source_dir_)
    source_dir = os.path.abspath(source_dir_)
    build_source_dir = os.path.join(build_dir, 'src')
    if not os.path.isdir(source_dir):
        console.logerror("Specified source space does not exist [" + source_dir + "]")
        sys.exit(1)
    if not os.path.isfile(os.path.join(source_dir, ".rosinstall")):
        console.logerror("Could not find a valid source folder (must contain a .rosinstall file therein)'")
        sys.exit(1)
    if os.path.exists(build_source_dir):
        if not source_dir == build_source_dir:
            console.error("The build directory already has a ./src directory which doesn't match the desired source directory [%s]" % source_dir)
            sys.exit(1)
    else:  # create a symlink to the sources
        common.symlink_dir(source_dir, build_source_dir)

    ##########################
    # Underlays
    ##########################
    env_underlays = os.environ['CMAKE_PREFIX_PATH']
    underlays_list = underlays_.split(';')
    env_underlays_list = env_underlays.split(':')
    for underlay in env_underlays_list:
        if underlay not in underlays_list:
            underlays_list.append(underlay)
    catkin_found = False
    for underlay in underlays_list:
        if os.path.isfile(os.path.join(underlay, 'bin', 'catkin_make')):
            catkin_make = os.path.join(underlay, 'bin', 'catkin_make')
            catkin_python_path = os.path.join(underlay, 'lib', 'python2.7', 'dist-packages')
            catkin_found = True
            break
    if not catkin_found:
        # Add the default track underlay
        default_track = common.get_default_track()
        if os.path.isfile(os.path.join("/opt/ros/%s" % default_track, 'bin', 'catkin_make')):
            console.pretty_println("No catkin found, adding the default track underlay [/opt/ros/%s]" % default_track)
            underlays_list.append("/opt/ros/%s" % default_track)
            catkin_make = os.path.join("/opt/ros/%s" % default_track, 'bin', 'catkin_make')
            catkin_python_path = os.path.join("/opt/ros/%s" % default_track, 'lib', 'python2.7', 'dist-packages')
        else:
            console.logerror("Could not find an underlying catkin installation.")
    underlays = ';'.join(underlays_list)

    ##########################
    # Toolchain
    ##########################
    toolchain = toolchain_
    if not toolchain_ == "":
        toolchains_dir = os.path.join(os.path.dirname(__file__), 'toolchains')
        if os.path.isfile(os.path.join(toolchains_dir, toolchain_ + ".cmake")):
            shutil.copy(os.path.join(toolchains_dir, toolchain_ + ".cmake"), os.path.join(build_dir, "toolchain.cmake"))
            toolchain = toolchain = "-DCMAKE_TOOLCHAIN_FILE=toolchain.cmake"

    ##########################
    # Platform
    ##########################
    if not platform_ == "":
        platforms_dir = os.path.join(os.path.dirname(__file__), 'platforms')
        if os.path.isfile(os.path.join(platforms_dir, platform_ + ".cmake")):
            shutil.copy(os.path.join(platforms_dir, platform_ + ".cmake"), os.path.join(build_dir, "platform.cmake"))

    ##########################
    # Other Args
    ##########################
    if install_prefix_ == "/not_set_directory":
        install_prefix = os.path.join(build_dir, "install")
    else:
        install_prefix = install_prefix_
    if release_:
        build_type = "Release"
    else:
        build_type = "DebugWithRelSymbols"
    name = os.path.basename(workspace_dir) + "_" + os.path.basename(build_dir)

    print_build_details(build_dir, source_dir, install_prefix, build_type, underlays, name, toolchain_, platform_)
    os.chdir(build_dir)

    ##########################
    # Cache
    ##########################
    instantiate_config_cmake(build_dir, install_prefix, underlays)

    ##########################
    # Templates
    ##########################
    instantiate_template('.bashrc', name, build_dir)
    instantiate_template('konsole', name, build_dir)
    instantiate_template('gnome-terminal', name, build_dir)
    instantiate_template('eclipse', name, build_dir)
    instantiate_makefile('Makefile', build_dir, os.path.relpath(source_dir, build_dir), catkin_make, catkin_python_path, toolchain)


def init_build():
    args = parse_arguments()
    ##########################
    # Tracks
    ##########################
    if args.get_default_track:
        console.pretty_print("\nDefault Track: ", console.cyan)
        console.pretty_println("%s\n" % common.get_default_track(), console.yellow)
        sys.exit(0)
    if args.set_default_track:
        console.pretty_print("\nNew Default Track: ", console.cyan)
        console.pretty_println("%s\n" % common.set_default_track(args.set_default_track), console.yellow)
        sys.exit(0)
    if not args.track:
        args.track = common.get_default_track()
    ##########################
    # Toolchains and Platform
    ##########################
    if args.list_toolchains:
        list_toolchains()
        sys.exit(0)
    if args.list_platforms:
        list_toolchains()
        sys.exit(0)
    init_configured_build(args.dir, args.sources, args.underlays, args.install, args.release, args.toolchain, args.platform)
