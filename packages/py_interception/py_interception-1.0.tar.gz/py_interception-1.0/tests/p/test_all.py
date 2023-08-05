'''
Created on Oct 1, 2012

@author: moi
'''
import unittest
from unittest import TestCase
import di
import interception as itc

@itc.intercepts(after=(itc.MethodExecuteInterceptor,))
class InterceptorA(itc.Interceptor):
    def intercept(self, stack, method_info, instance, *args, **kwargs):
        method_info.result += ":A"
        stack.next()

@itc.intercepts(before=(InterceptorA,), after=(itc.MethodExecuteInterceptor,))
class InterceptorB(itc.Interceptor):
    def intercept(self, stack, method_info, instance, *args, **kwargs):
        method_info.result += ":B"
        stack.next()

@di.comp()
class Controller(object):
    def teste_method(self, *args, **kwargs):
        return ":C"

class InterceptionTest(TestCase):
    def test_method_execute(self):
        container = di.Container()
        container.components[Controller] = Controller
        
        registry = itc.InterceptorRegistry(container)
        registry += itc.MethodExecuteInterceptor
        
        method_info = itc.MethodInfo(Controller, Controller.teste_method)
        
        instance_creator = itc.InstanceCreator(container)
        stack = itc.Stack(registry.sorted(), itc.StackExecutor(method_info, instance_creator))
        stack.next()
        
        assert ":C" == method_info.result
        
    def test_with_interceptors(self):
        container = di.Container()
        container.components[Controller] = Controller
        
        registry = itc.InterceptorRegistry(container)
        registry += itc.MethodExecuteInterceptor
        registry += InterceptorA
        registry += InterceptorB
        
        method_info = itc.MethodInfo(Controller, Controller.teste_method)
        
        instance_creator = itc.InstanceCreator(container)
        stack = itc.Stack(registry.sorted(), itc.StackExecutor(method_info, instance_creator))
        stack.next()
        
        assert ":C:B:A" == method_info.result

if __name__ == "__main__":
    unittest.main()
