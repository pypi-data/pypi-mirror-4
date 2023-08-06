"""
recursely :: Recursive importer for Python submodules
"""
__version__ = "0.0.1"
__author__ = "Karol Kuczmarski"
__license__ = "BSD"


import imp
import os
import sys

from .hook import ImportHook
from .utils import SentinelList


def install():
    """Install the recursive import hook in ``sys.meta_path``.

    Because the hook is a catch-all one, we ensure that it's always
    at the very end of ``sys.meta_path``, so that it's tried only if
    no other (more specific) hook has been chosen by Python.
    """
    imp.acquire_lock()
    try:
        sys.meta_path = SentinelList(sys.meta_path,
                                     sentinel=RecursiveImporter())
    finally:
        imp.release_lock()


class RecursiveImporter(ImportHook):
    """Hook for recursive import of submodules and subpackages
    of a package that is marked as 'recursive'.

    In general, such packages should have ``__recursive__ = True``
    somewhere inside their `__init__.py` files.
    """
    def on_module_imported(self, fullname, module):
        """Invoked just after a module has been imported."""
        recursive = getattr(module, '__recursive__', None)
        if recursive:
            return self._recursive_import(module)

    def _recursive_import(self, module):
        """Recursively import submodules and/or subpackage of given package.
        :param module: Module object for the package's `__init__` module
        """
        package_dir = self._get_package_dir(module)
        if not package_dir:
            return

        children = self._list_children(package_dir)
        if children:
            globals_ = module.__dict__
            locals_ = module.__dict__
            for child in children:
                child_module = __import__(child, globals_, locals_)
                if not hasattr(module, child):
                    setattr(module, child, child_module)

                # apply the importing procedure recursively,
                # but only if it wasn't applied already, simply by
                # our import hook triggering when child was imported above
                if not hasattr(child_module, '__recursive__'):
                    self._recursive_import(child_module)

        module.__loader__ = self
        return module

    def _get_package_dir(self, module):
        """Get the package directory for given `__init__` module."""
        module_file = getattr(module, '__file__', None)
        if not self._is_init_py(module_file):
            return
        return os.path.dirname(module_file)

    def _is_init_py(self, module_file):
        """Check if given filename points to an `__init__` module."""
        if not module_file:
            return False

        filename = os.path.basename(module_file)
        root, _ = os.path.splitext(filename)
        return root == '__init__'

    def _list_children(self, package_dir):
        """Lists all child items contained with given package
        including submodules and subpackages

        :param package_dir: Package directory
        """
        children = []
        children.extend(self._list_subpackages(package_dir))
        children.extend(m for m in self._list_submodules(package_dir)
                        if m != '__init__')
        return children

    def _list_subpackages(self, package_dir):
        """Lists all subpackages (directories with `__init__.py`)
        contained within given package.

        :param package_dir: Package directory
        """
        def is_subpackage_dir(name):
            abs_path = os.path.join(package_dir, name)
            init_py = os.path.join(abs_path, '__init__.py')
            return os.path.isdir(abs_path) and os.path.isfile(init_py)

        return [name for name in os.listdir(package_dir)
                if is_subpackage_dir(name)]

    def _list_submodules(self, package_dir):
        """Lists all submodules (`*.py` files) contained within given package.
        :param package_dir: Package directory
        """
        def is_submodule_file(name):
            abs_path = os.path.join(package_dir, name)
            return os.path.isfile(abs_path) and name.endswith('.py')

        return [os.path.splitext(name)[0]
                for name in os.listdir(package_dir)
                if is_submodule_file(name)]
