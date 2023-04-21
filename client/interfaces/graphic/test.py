class A:
    @property
    def field(self):
        return 1
    
    def f(self):
        return self.g()
    
    def g(self):
        return 1
    
class B(A):
    @property
    def field(self):
        return 2
    
    def g(self):
        return 2
    
print(B().f())