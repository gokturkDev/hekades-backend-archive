from typing import Protocol


class A(Protocol):
    def test(self, content: str):
        ...


class B:
    def test(self, content: str):
        content += "Protocols are an alternative to ABC subtyping"
        return content


def fun(x: A):
    x.test("Hello World")


def test_protocol():
    fun(B())
