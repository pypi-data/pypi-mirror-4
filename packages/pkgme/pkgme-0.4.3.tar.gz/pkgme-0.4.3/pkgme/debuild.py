import os
import re

from debian.changelog import Changelog

from pkgme.run_script import run_subprocess


def find_changes_file(output_lines,
                      _changes_file_re=re.compile(r' dpkg-genchanges -S >(.*)')):
    for line in output_lines:
        match = _changes_file_re.match(line)
        if match:
            return match.group(1)
    raise ValueError("Could not find changes filename")


def _find_binary_files_in_dir(directory):
    """Return a list of binary files in a given directory

    A file is considered binary if it has a \0 in the first 4k of its data.
    This is the same algorithm that "grep" is using.
    """
    bin_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # test if its a binary file,
            # this is what grep is doing to identify binary files
            if "\0" in open(os.path.join(dirpath, filename)).read(4*1024):
                bin_files.append(
                    os.path.relpath(os.path.join(dirpath, filename), directory))
    return bin_files


def build_debian_source_include_binaries_content(directory):
    """Inspect the directory for binary files in the debian dir and
       add them to debian/source/include-binaries

    This is needed in the non-native dpkg "3.0 (quilt)" source format
    to include binary data like icons.
    """
    debian_dir = os.path.join(directory, "debian")
    bin_files = [os.path.join("debian", p)
                 for p in _find_binary_files_in_dir(debian_dir)]
    with open(os.path.join(
            directory, "debian/source/include-binaries"), "w") as f:
        f.write("\n".join(bin_files))


def build_source_package(directory, sign=True):
    """Build a source package using debuild"""
    # prepare the debian/dir by adding binary files to
    #    debian/source/include-binaries
    #
    # this is essentially what the following is doing:
    #    "debuild --source-option=--include-binaries"
    # but that option is only available on natty and later (not lucid)
    #
    # once we do no longer support lucid this can go
    build_debian_source_include_binaries_content(directory)
    # now build the orig.tar.gz
    build_orig_tar_gz(directory)
    # and then the package itself
    cmd = ['debuild', '--no-lintian', '-S']
    if not sign:
        cmd.extend(['-uc', '-us'])
    output = run_subprocess(cmd, cwd=directory)
    changes_file = find_changes_file(output)
    return os.path.abspath(os.path.join(directory, changes_file))


def build_orig_tar_gz(target_dir):
    """Build a pkgname_version.orig.tar.gz from the target_dir.

    This is usually run as part of build_source_package and does
    rarely need to be run on its own.

    Note that this will expect a debian/ directory in the target_dir
    to gather pkgname/version but it will (of course) exclude debian/
    from the resulting .orig.tar.gz
    """
    changelog = Changelog(
        open(os.path.join(target_dir, "debian", "changelog")))
    pkgname = changelog.get_package()
    version = changelog.get_version()
    target_file = os.path.join(
        target_dir, "..", "%s_%s.orig.tar.gz" % (pkgname, version))
    cmd = ["tar",
           "-c",
           "-z",
           "--exclude", "./debian",
           # "S" flag means "don't transform symlink targets"
           "--transform", "s,.,%s-%s,S" % (pkgname, version),
           "-f", target_file,
           ".",
           ]
    run_subprocess(cmd, cwd=target_dir)
    return target_file
