"""import a set of files from a file-system into a repository"""
import os
import shutil

from mercurial import commands, hg, util
from mercurial.error import Abort, RepoError
from mercurial.i18n import _

__version__ = '1.3.2'


def get_repo(ui, path):
    """Initialize or create a repository."""
    try:
        repo = hg.repository(ui, path)
    except RepoError:
        repo = hg.repository(ui, path, True)
        ui.status(_('created repository %s\n') % repo.root)
    return repo


def update_repo(ui, repo, rev, branch=None):
    """Update the repository using the --clean option.

    Creates a new branch if necessary.
    """
    if branch:
        if branch not in repo.branchmap():
            # Create a named branch.
            commands.update(ui, repo, rev=rev, clean=True)
            commands.branch(ui, repo, label=branch)
        else:
            # Update to the named branch.
            commands.update(ui, repo, rev=branch, clean=True)
    elif rev:
        # Create an anonymous branch.
        commands.update(ui, repo, rev=rev, clean=True)
        commands.branch(ui, repo)
    elif repo.dirstate.branch() != 'default':
        # Update to the default branch.
        commands.update(ui, repo, rev='default', clean=True)
    else:
        commands.update(ui, repo, clean=True)


def onerror(func, path, exc_info=tuple()):
    """Error handler for shutil.rmtree and methods of the os package.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    """
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def purge_repo(repo):
    """Empty the repository except the metadata."""
    for node in os.listdir(repo.root):
        if node.startswith('.hg'):
            continue
        path = os.path.join(repo.root, node)
        if os.path.isdir(path):
            shutil.rmtree(path, onerror=onerror)
        else:
            try:
                os.remove(path)
            except WindowsError:
                onerror(os.remove, path)


def contains_backslashes(path):
    """Resolves a symlink and checks if the path contains backslashes."""
    return '\\' in os.readlink(path)


def replace_backslashes(path):
    """Replaces all backslashes in a symlink target with slashes.

    Returns the symlink's target.
    """
    return os.readlink(path).replace('\\', '/')


def dereference_symlink(path):
    """Returns a dereferenced symlink.

    If the symlink contains backslashes they are replaced with slashes.
    """
    linkto = replace_backslashes(path)
    return os.path.join(os.path.dirname(path), linkto)


def smartcopy(ui, src, dst, node, ignore=None, exclude_path=None, no_errors=False):
    """Copies a node (recursively) from src to dst directory.

    If node is a file only the file is copied.

    If node is a directory the entire directory tree is copied recursively. The
    destination directory must not already exist; it will be created as well as
    missing parent directories.

    If ignore is given, it must be a callable that will receive as its
    arguments the directory being visited by smartcopy(), and a list of its
    contents, as returned by os.listdir(). Since smartcopy() is called
    recursively, the ignore callable will be called once for each directory
    that is copied. The callable must return a sequence of directory and file
    names relative to the current directory (i.e. a subset of the items in its
    second argument); these names will then be ignored in the copy process.
    shutil.ignore_patterns() can be used to create such a callable that ignores
    names based on glob-style patterns.

    If given, exclude_path must be a list of paths relative to src (no leading
    slash!). All paths exactly matching an element of exclude_path will be
    ignored.

    If no_errors is True all errors will be returned as a list of warnings.
    """
    srcpath = os.path.join(src, node)
    dstpath = os.path.join(dst, node)
    warnings = []
    error_msg = 'Failed to copy %s to %s (%s).\n'
    # Use exclude options.
    if node in exclude_path:
        # Terminate immediately if node is in the exclude path list.
        return warnings
    if ignore is not None:
        if len(ignore(src, (node,))) > 0:
            # Terminate immediately if the node matches the exclude pattern.
            return warnings
    # Either create a symlink or copy the files recursively.
    is_symlink = os.path.islink(srcpath)
    symlinks = True
    if os.name == 'nt':
        # Dereference symlinks for Windows.
        symlinks = False
    if symlinks and is_symlink:
        if contains_backslashes(srcpath):
            symlinks = False
            oldsrc = srcpath
            srcpath = dereference_symlink(srcpath)
            ui.debug(_('dereferenced %s to %s\n') % (oldsrc, srcpath))
    if symlinks and is_symlink:
        linkto = os.readlink(srcpath)
        ui.debug(_('creating symlink %s -> %s\n') % (dstpath, linkto))
        os.symlink(linkto, dstpath)
    else:
        try:
            if os.path.isdir(srcpath):
                copytree(ui, srcpath, dstpath, symlinks, ignore, exclude_path)
            else:
                ui.debug(_('copying %s to %s\n') % (srcpath, dstpath))
                shutil.copy(srcpath, dstpath)
        except shutil.Error, err:
            errors = []
            for error in err.args[0]:
                errors.append(error_msg % error)
            if no_errors:
                warnings += errors
            else:
                raise Abort(', '.join(errors))
        except OSError, err:
            if no_errors:
                warnings.append(error_msg % (srcpath, dstpath, err))
            else:
                raise
    return warnings


def get_common_suffix(path1, path2):
    """Takes two paths and returns the common suffix.

    If the common suffix has a leading directory separator it's removed.
    """
    common_chars = []
    path1 = list(path1)
    path2 = list(path2)
    while len(path1) > 0:
        char1 = path1.pop()
        char2 = path2.pop()
        if char1 == char2:
            common_chars.insert(0, char1)
        else:
            break
    common_suffix = ''.join(common_chars).lstrip(os.sep)
    return common_suffix


def copytree(ui, src, dst, symlinks=False, ignore=None, exclude_path=None):
    """Recursively copy an entire directory tree rooted at src. The destination
    directory, named by dst, must not already exist; it will be created as well
    as missing parent directories. Permissions and times of directories are
    copied with copystat(), individual files are copied using copy2().

    If symlinks is true, symbolic links in the source tree are represented as
    symbolic links in the new tree; if false or omitted, the contents of the
    linked files are copied to the new tree.

    If ignore is given, it must be a callable that will receive as its
    arguments the directory being visited by copytree(), and a list of its
    contents, as returned by os.listdir(). Since copytree() is called
    recursively, the ignore callable will be called once for each directory
    that is copied. The callable must return a sequence of directory and file
    names relative to the current directory (i.e. a subset of the items in its
    second argument); these names will then be ignored in the copy process.
    ignore_patterns() can be used to create such a callable that ignores names
    based on glob-style patterns.

    If the suffix of a file or directory in src matches a string in the
    exclude_path list it's not copied.

    If exception(s) occur, an Error is raised with a list of reasons.
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    ui.debug(_('creating directory %s\n') % dst)
    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if exclude_path is not None:
            common_suffix = get_common_suffix(srcname, dstname)
            if common_suffix in exclude_path:
                continue
        try:
            is_symlink = os.path.islink(srcname)
            if is_symlink:
                if contains_backslashes(srcname):
                    symlinks = False
                    oldsrc = srcname
                    srcname = dereference_symlink(srcname)
                    ui.debug(_('dereferenced %s to %s\n') % (oldsrc, srcname))
            if symlinks and is_symlink:
                linkto = os.readlink(srcname)
                ui.debug(_('creating symlink %s -> %s\n') % (dstname, linkto))
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(ui, srcname, dstname, symlinks, ignore, exclude_path)
            else:
                ui.debug(_('copying %s to %s\n') % (srcname, dstname))
                shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)


def create_empty_file(name, dirname, names):
    """Creates an empty file named "name" in dirname if dirname is empty.

    This solves the problem of adding empty directories to a repository.
    """
    if len(names) == 0:
        empty_file = os.path.join(dirname, name)
        with open(empty_file, 'w'):
            pass


def importfs(ui, repo, source, *pats, **opts):
    """Import a set of files from a file-system into a repository.

    Imports a set of files from a given file-system into a Mercurial
    repository as a changeset. If anything fails, the program exits, leaving
    the repository as it is.

    The specified repository is created if it doesn't exist. It is updated to
    the specified parent revision or tip.

    If the repository is updated to a revision other than "tip" the new
    revision is created on a new branch. If the branch option is used the
    branch has the given name. Otherwise the name "default" is used.

    The files in the working directory are deleted and the files from the
    source directories are copied into the working directory. If a file exists
    in more than one source directory the file in the rightmost directory wins.
    "hg addremove" with the specified similarity is executed. "hg commit" with
    the specified message is executed. If a tag is specified, "hg tag" with the
    name is executed.

    If the import is done in Windows, symbolic links are dereferenced
    - that is, replaced by a copy of the linked file or directory. If the
    import is done in Unix, symbolic links are imported as Unix symbolic
    links (i.e. not dereferenced).

    All files and directories matching the exclude pattern will be ignored. If
    you want to use more than one pattern use the --exclude-pattern option
    several times. The following example will copy everything except .pyc files
    and files or directories whose name starts with tmp.

    $ hg importfs repo source --exclude-pattern *.pyc --exclude-pattern tmp

    The --exclude-path option takes an exact path as value. The result is that
    the files in the path are not imported. The option can be used several
    times for different paths. The path is specified relative to SOURCE.

    Using the --retain-empty-dirs option will create a new file, .empty, during
    the import when a empty directory is encountered so that the directory is
    added to the repository. This is executed after the contents of the SOURCE
    are determined (e.g. after the exclude options are applied).
    """
    sources = []
    for node in (source,) + pats:
        path = util.expandpath(node)
        if not os.path.exists(path):
            raise Abort(_('directory %s does not exist') % path)
        sources.append(path)
    repo = get_repo(ui, repo)
    # The repository is purged before the update because there can be files
    # without write permissions and Mercurial fails to update them.
    purge_repo(repo)
    update_repo(ui, repo, opts.get('rev'), opts.get('branch'))
    purge_repo(repo)
    # Prepare exclusion rules.
    exclude_path = opts.get('exclude_path')
    exclude_pattern = opts.get('exclude_pattern')
    if exclude_pattern:
        ignore = shutil.ignore_patterns(*exclude_pattern)
    else:
        ignore = None
    # Copy all files into the repository.
    for sourcepath in sources:
        for node in os.listdir(sourcepath):
            warnings = smartcopy(ui, sourcepath, repo.root, node, ignore,
                exclude_path, opts.get('ignore_copy_errors'))
            if len(warnings) == 0:
                continue
            # Print warnings. This will only happen if smartcopy was called
            # with the ignore_copy_errors option set to True.
            for warning in warnings:
                ui.write('Warning: ' + warning)
    if opts.get('retain_empty_dirs') is True:
        os.path.walk(repo.root, create_empty_file, '.empty')
    commands.addremove(ui, repo, similarity=opts.get('similarity'))
    message = opts.get('message') or 'importfs commit.'
    commands.commit(ui, repo, message=message)
    tag = opts.get('tag')
    if tag:
        commands.tag(ui, repo, tag)


cmdtable = {'importfs':
    (importfs,
    [('r', 'rev', '', _('The revision to use as the immediate predecessor of '
        'the new revision. If omitted tip is used.'), _('REV')),
    ('b', 'branch', '', _("The name of a branch for the new revision. If it "
        "doesn't exist it is created. If omitted the default branch is used. "
        "This option is required if a revision other than tip is specified."),
        _('NAME')),
    ('s', 'similarity', 100, _('A number to pass as the value of the '
        'similarity option to "hg addremove" for guessing file renames. (See '
        'hg help for an explanation.) If omitted the value "100" is used.'),
        _('SIMILARITY')),
    ('m', 'message', '', _('The commit message to be used. If omitted the '
        'tag string is used.'), _('TEXT')),
    ('t', 'tag', '', _('The tag for the resulting revision. If omitted the '
        'revision is not tagged.'), _('NAME')),
    ('', 'exclude-pattern', list(),
        _('Exclude all files matching the given pattern.'), _('PATTERN')),
    ('', 'exclude-path', list(),
        _('Exclude the exact path relative to SOURCE.'), _('PATH')),
    ('', 'ignore-copy-errors', None, _('Turn all errors during the file copy '
        'operation into warnings.')),
    ('', 'retain-empty-dirs', None,
        _('Add empty directories to the repository.'))],
    '[OPTION]... REPO SOURCE...')
}
commands.norepo += ' importfs'


testedwith = '1.8 1.8.1 1.8.2 1.8.3 1.8.4 1.9 1.9.1 1.9.2 1.9.3'
testedwith += ' 2.0 2.0.1 2.0.2 2.1 2.1.2 2.2 2.2.1 2.2.2 2.2.3 2.3 2.3.1 '
testedwith += ' 2.3.2 2.4'

buglink = 'https://bitbucket.org/keimlink/hg-importfs/issues'
