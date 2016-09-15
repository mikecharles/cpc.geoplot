#!/usr/bin/env python
import os, sys
import re
import subprocess
import pkgutil


def list_submodules(submodules_list, package):
    """
    Lists all the submodules in the given package.

    Nothing is returned from this function; it will instead append the names (as strings) of all
    submodules found in the given package to `submodules_list`.

    ### Parameters

    - submodules_list (list): list to append module names to
    - package (module): package to find submodules in
    """
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__+'.'):
        submodules_list.append(module_name)
        module_name = __import__(module_name, fromlist='dummylist')
        if is_pkg and module_name != package.__name__:
            list_submodules(submodules_list, module_name)


def write_module_api(module_name, parent_dir='.', out_file=None, remove_top_level=True,
                     customize_formatting=False):
    """
    Writes API documentation for a given module to a Markdown file.

    The name of the Markdown file is determined by the hierarchy given in the module name (using
    dots). The top-level package name is removed from the module name (if `remove_top_level=True`),
    and every dot is converted to a forward slash, which results in a path to a file (once '.md'
    is appended).

    For example, API documentation for the module `sound.effects.echo` would be written to
    `./effects/echo.md` (or `./sound/effects/echo.md` if `remove_top_level=False`).

    ### Parameters

    - module_name (*string*): name of module to write API documentation for
    - parent_dir (*string*, default='.'): parent directory to write API documentation to
    - out_file (*string*, default=None): Markdown file to write to (if None, determine
      automatically using the name of the module)
    - remove_top_level (*boolean*, default=True): remove the top level of the module name when
      determining the out_file
    - customize_formatting (*boolean*, default=False): customize the default Markdown written by
      the `pydoc-markdown` module
    """
    print('pydoc-markdown {}'.format(module_name))
    try:
        output = subprocess.check_output('pydoc-markdown {}'.format(module_name), shell=True).decode(
            'ascii')
    except:
        return
    # Customize formatting (optional)
    if customize_formatting:
        # Make functions/classes non-inline code level 3 headings instead of inline code level 5
        # headings
        regex = re.compile(r'^##### `(__.*)`', flags=re.MULTILINE)  # dunder functions
        replacement = '### <span class="function">\\\\\g<1></span>'
        output = regex.sub(replacement, output)
        regex = re.compile(r'^##### `(.*)`', flags=re.MULTILINE)  # non-dunder functions
        replacement = '### <span class="function">\g<1></span>'
        output = regex.sub(replacement, output)

    # Write output to file
    if out_file is None:
        if remove_top_level:
            out_file_full = re.sub('^{}\.'.format(main_package_name), '', module_name) + '.md'
        else:
            out_file_full = module_name + '.md'
        out_file_full = parent_dir + '/' + out_file_full
    out_dir = os.path.dirname(out_file_full)
    out_file = os.path.basename(out_file_full)
    print('Writing output to {}/{}...'.format(out_dir, out_file))
    os.makedirs(out_dir, exist_ok=True)
    with open(out_dir + '/' + out_file, 'w') as f:
        jekyll_front_matter = '''---
layout: default
title: {} module
type: apidoc
---
        '''.format(module_name)
        f.write(jekyll_front_matter)
        f.write(output)
    # Prepend Jekyll front matter


# Get command-line args
if len(sys.argv) < 2:
    print('Usage: {} [PACKAGE-NAME]'.format(os.path.basename(__file__)))
    sys.exit(1)
else:
    main_package_name = sys.argv[1]

try:
    parent_dir = sys.argv[2]
except IndexError:
    parent_dir = 'api'

# Try importing the package to find submodules in
try:
    package = __import__(main_package_name, fromlist='dummylist')
except ImportError:
    print('Package {} not found...'.format(main_package_name))
    sys.exit(1)

# Initialize list of modules
all_submodules = []
list_submodules(all_submodules, package)

for submodule_name in all_submodules:
    write_module_api(submodule_name, parent_dir=parent_dir, customize_formatting=True)
