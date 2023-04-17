class A:
    class C:
        @staticmethod
        def f():
            print(1)

    def g(self):
        # self.__class__.C.f()
        self.h()

    def h(self):
        print(1)


class B(A):
    class C:
        @staticmethod
        def f():
            print(2)

    def g(self):
        # self.__class__.C.f()
        # super().g()
        super().h()

    def h(self):
        print(2)


B().g()
print(isinstance(3, float))