'''
Python Container Of Dependency Injection Interception implementation

Created on Sep 26, 2012

@author: Moises P. Sena <moisespsena@gmail.com>
'''
import di
from sdag2 import DAG

class InterceptorItem(object):
    def __init__(self, interceptor, before=None, after=None):
        self.interceptor = interceptor
        self.before = before
        self.after = after

class InstanceCreator(object):
    def __init__(self, container):
        self.container = container

    def normal_instance_for(self, key_or_cls):
        return self.container.instance_for(key_or_cls)

    def lazy_instance_for(self, interceptor):
        component = di.decorator.of(di.comp, intercepts)
        deps = dict()
        if component:
            deps = component.deps_none

        obj = interceptor(**deps)

        def normal_instance():
            return self.normal_instance_for(interceptor)

        obj = _LazyInterceptor(obj, normal_instance)
        return obj

    def instance_for(self, key_or_cls, lazy=False):
        if lazy:
            return self.lazy_instance_for(key_or_cls)
        else:
            return self.normal_instance_for(key_or_cls)

class InterceptorRegistry(object):
    def __init__(self, container):
        self.interceptors = set()
        self.container = container

    def __add__(self, item):
        self.add(item)
        self.container.components[item] = item
        return self

    def add(self, interceptor, before=None, after=None):
        intercepts_obj = di.decorator.of(interceptor, intercepts)

        if intercepts_obj:
            if not before:
                before = intercepts_obj.before
            if not after:
                after = intercepts_obj.after

        item = InterceptorItem(interceptor, before=before, after=after)
        self.interceptors.add(item)

    def __contains__(self, key):
        return self.has(key)

    def has(self, key):
        return key in self.interceptors

    def key(self, interceptor):
        return "%s.%s" % (interceptor.__module__, interceptor.__name__)

    def sorted(self):
        dag = DAG()
        imap = dict()
        vmap = dict()
        
        for _ in self.interceptors:
            k = self.key(_.interceptor)
            imap[k] = _
            vmap[k] = dag.add(k)
            
        for k in imap:
            _ = imap[k]
            v = vmap[k]
            
            if _.before:
                for o in _.before:
                    o = vmap[self.key(o)]
                    dag.add_edge(v, o)
            
            if _.after:
                for o in _.after:
                    o = vmap[self.key(o)]
                    dag.add_edge(o, v)
                
        rs = dag.topologicaly()
        s = [imap[k].interceptor for k in rs]
        return s
    
class intercepts(di.comp):
    def __init__(self, lazy=False, after=(), before=()):
        super(intercepts, self).__init__()
        self.after = set(after)
        self.before = set(before)
        self.lazy = lazy
        
class MethodSearch(object):
    def __init__(self, searcher=None):
        self.searcher = searcher
    
    def search(self, query):
        if self.searcher:
            return self.searcher(query)
        else:
            return self.default_searcher(query)
    
    def default_searcher(self, query):
        parts = query.split('.')
        cls_name = ".".join(parts[:-1])
        method_name = parts[-1:]
        
        cls = di.import_class(cls_name)
        method = getattr(cls, method_name)
        return method

class MethodInfo(object):
    def __init__(self, cls=None, method=None, obj=None, args=(), kwargs=dict()):
        self.cls = cls
        self.method = method
        self.obj = obj
        self.args = args
        self.kwargs = kwargs
        self.result = None

class StackExecutor(object):
    def __init__(self, method_info, instance_creator):
        self.method_info = method_info
        self.instance_creator = instance_creator
        
    def intercept(self, stack, interceptor):
        instance = self.instance_creator.instance_for(self.method_info.cls)
        obj = self.instance_creator.instance_for(interceptor, False)
        obj.intercept(stack, self.method_info, instance)
        
    def execute(self, stack, interceptor):
        dec = di.decorator.of(interceptor, intercepts)
        obj = self.instance_creator.instance_for(interceptor, dec.lazy)
        
        if obj.accepts(self.method_info):
            self.intercept(stack, interceptor)

class Stack(object):
    def __init__(self, interceptors, executor):
        self.interceptors = interceptors
        self.prev_index = -1
        self.index = 0
        self.last_index = len(self.interceptors) - 1
        self.executor = executor
        
    def next(self):
        if self.index <= self.last_index:
            self.prev_index += 1
            self.index += 1
            interceptor = self.interceptors[self.prev_index]
            self.executor.execute(self, interceptor)
        
class Interceptor(object):
    def accepts(self, *args, **kwargs):
        return True
    
    def intercept(self, stack, method_info, instance, *args, **kwargs):
        stack.next()

class _LazyInterceptor(Interceptor):
    def __init__(self, lazy_obj, instance_creator):
        self.lazy_obj = lazy_obj
        self.instance_creator = instance_creator
        
    def accepts(self, *args, **kwargs):
        return self.lazy_obj.accepts(*args, **kwargs)
    
    def intercept(self, *args, **kwargs):
        obj = self.instance_creator()
        return obj.intercept(*args, **kwargs)

@intercepts(lazy=True)
class MethodExecuteInterceptor(Interceptor):
    def intercept(self, stack, method_info, instance, *args, **kwargs):
        result = method_info.method(instance, *method_info.args, **method_info.kwargs)
        method_info.result = result
        stack.next()
