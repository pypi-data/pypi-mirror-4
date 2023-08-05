Changelog
=========

1.3.2
-----

- Tested with 2.2.3, 2.3, 2.3.1, 2.3.2, 2.4
- Updated documentation
- Added links to issue tracker

1.3.1
-----

- Improved installation instructions

1.3.0
-----

- Changed package name to hg-importfs (as initially intended)

1.2.3
-----

- Changelog appears now at the of package description
- Added repository and PyPI urls to README

1.2.2
-----

- Removed reStructuredText header from CHANGELOG.rst

1.2.1
-----

- Updated README to render as reStructuredText on PyPI

1.2.0
-----

- First Open Source release!
- Added testedwith variable
- Test suite works now with Mercurial 2.2.x
- Added installation instructions and example to README
- Moved development information to README

1.1.0
-----

- Symlinks are no longer dereferenced on Linux (but still dereferenced on
  Windows).
- If the path of a symlink on Linux contains backward slashes (i.e. the link
  was intended for Windows), the slashes are converted to forward slashes and
  the link is dereferenced.
- Renamed --exclude option to --exclude-pattern.
- Added new option --exclude-path to exclude a path relative to SOURCE.
- Added new option --retain-empty-dirs to import empty directories.
- The update operation inside the repository is using the --clean option.
- The repository is purged before each update/commit because there can be files
  without write permissions and Mercurial fails to update them.

1.0.1
-----

- Write warnings on ignored copy errors to stdout instead of stderr.
- Using a slash as new exclude pattern separator.

1.0
---

- Added new options exclude and ignore-copy-errors.

0.9
---

- Allow to create anonymous branches.

0.8.1
-----

- Fixed the problem with wrong permissons of single files in the root of the
  repo on Windows.

0.8
---

- Changed filesystem operations to be OS independent. Extension can now be used on Windows.
- SOURCE can now be a list of directories.

0.7.1
-----

- Fixed the version number (which was still 0.6 for the 0.7 release).

0.7
---

- Removed the "dereference" option.

0.6
---

- Fixed missing updates. The repository wasn't always at the lastest revision
  when doing the import.
- Added new option "dereference" to follow symlinks.
- Updated package classifiers.
- Added this Changelog.
- Added long_description to package metadata.

0.5.1
-----

- Removed importfs.py from MANIFEST.in.

0.5
---

- Initial release.
