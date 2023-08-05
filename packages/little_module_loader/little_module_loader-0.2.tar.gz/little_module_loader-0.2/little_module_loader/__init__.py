""" Provides a few functions for loading modules (and classes) from a package

    Examples
    ---------
    
    Finding modules based on filename::
    
        import little.module_loader
        parent = "petit"
        
        dict(little.module_loader.find(parent, lambda x: x.endswith("_subsystem.py")))
        # this returns a dictionary that maps name of module (without parent) and the actual module object
            
    Finding all classes that are subclasses of another class::
    
        dict(class_finder("petit.packets", Packet))
        # this returns a dictionary that maps the name of the class to the class object for instantiation
"""
import os.path as path
import types
from pkg_resources import resource_listdir
import importlib

def _load_module(parent_package, module_name):
    """ Load a module from a parent package.  Return None if it cannot be found
    
        :param parent_package: The name of the parent package
        :param_type parent_package: string
        :param module_name: The name of the module to load
        :param_type module_name: string
    """
    try:
        full_module_name = "{parent_package}.{module_name}".format(parent_package=parent_package,
                                                           module_name=module_name)

        module = importlib.import_module(full_module_name)
        return module
    except ImportError,ex:
        print ex
        return None

def find(parent_package, predicate):
    """ Find all modules in the specified parent package
        
        :param parent_package: The name of the parent package
        :type parent_package: string
        :param predicate: A callable that takes the module name
        :type predicate: callable
        
        :returns: a list of tuples in the form (module name, module object)
    """ 
    for system in filter(predicate, resource_listdir(parent_package, '')):
        (module_name, ext) = path.splitext(system)
        if ext == ".py":
            retval = _load_module(parent_package, module_name)
            if retval is not None:
                yield (module_name, retval)
                
def class_finder(parent_package, parent_class, predicate = lambda x: not x.endswith('__init__.py')):
    """ Find all classes that are inherited from a parent class
    
        :param parent_package: The name of the parent package
        :type parent_package: string
        :param parent_class: The parent class to look for
        :type parent_class: class
        :param predicate: A callable that takes the module name
        :type predicate: callable

        
        :returns: a list of tuples in the form (class name, class object)
    """
    
    for (name, module) in find(parent_package, predicate):
        for x in [getattr(module, y) for y in dir(module)]:
            if types.TypeType == type(x) and issubclass(x, parent_class):
                yield (x.__name__, x)

def function_finder(parent_package, function_name, predicate = lambda x: not x.endswith('__init__.py')):
    """ Find all specifically named functions in all modules in a package
    
        :param parent_package: The name of the parent package
        :type parent_package: string
        :param parent_class: The parent class to look for
        :type parent_class: class
        :param predicate: A callable that takes the module name
        :type predicate: callable
        
        :returns: a list of tuples in the form (function name, function object)
    """
    for (name, module) in find(parent_package, predicate):
        for x in [getattr(module, y) for y in dir(module) if y == function_name]:
            if callable(x):
                yield(x.__name__, x)