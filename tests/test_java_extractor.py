from analyzer.java_extractor import extract_methods_from_source


def test_extract_methods_basic():
    source = """
    public class Test {
        /**
         * Saluda a una persona
         * @param name nombre
         * @return saludo
         */
        public String hello(String name) {
            return "Hello " + name;
        }

        public void ping() {
            System.out.println("pong");
        }
    }
    """

    methods = extract_methods_from_source(source)

    assert len(methods) == 2

    hello = methods[0]
    ping = methods[1]

    assert hello.method_name == "hello"
    assert hello.javadoc.exists is True
    assert hello.javadoc.description == "Saluda a una persona"

    assert ping.method_name == "ping"
    assert ping.javadoc.exists is False


def test_multiple_parameters():
    source = """
    public class Test {
        /**
         * Suma valores
         * @param a primero
         * @param b segundo
         * @return resultado
         */
        public int sum(int a, int b) {
            return a + b;
        }
    }
    """

    methods = extract_methods_from_source(source)
    method = methods[0]

    assert len(method.parameters) == 2
    assert method.parameters[0].name == "a"
    assert method.parameters[1].name == "b"

    assert len(method.javadoc.params) == 2


def test_method_without_parameters():
    source = """
    public class Test {
        public void ping() {
            System.out.println("pong");
        }
    }
    """

    methods = extract_methods_from_source(source)
    method = methods[0]

    assert method.parameters == []


def test_method_without_javadoc():
    source = """
    public class Test {
        public String hello() {
            return "hi";
        }
    }
    """

    methods = extract_methods_from_source(source)
    method = methods[0]

    assert method.javadoc.exists is False


def test_void_method_without_return_tag():
    source = """
    public class Test {
        /**
         * Hace algo
         */
        public void doSomething() {
            System.out.println("x");
        }
    }
    """

    methods = extract_methods_from_source(source)
    method = methods[0]

    assert method.return_type == "void"
    assert method.javadoc.return_value == ""


def test_incomplete_javadoc():
    source = """
    public class Test {
        /**
         * Hace algo
         */
        public int calc(int a) {
            return a * 2;
        }
    }
    """

    methods = extract_methods_from_source(source)
    method = methods[0]

    assert method.javadoc.exists is True
    assert method.javadoc.description == "Hace algo"
    assert method.javadoc.params == []


def test_private_method_extraction():
    source = """
    public class Test {
        private String normalize(String value) {
            return value.trim();
        }
    }
    """

    methods = extract_methods_from_source(source)

    assert len(methods) == 1
    assert methods[0].method_name == "normalize"


def test_ignore_method_without_body():
    source = """
    public abstract class Test {
        public abstract void doSomething();
    }
    """

    methods = extract_methods_from_source(source)

    assert len(methods) == 0


def test_multiline_javadoc_description():
    source = """
    public class Test {
        /**
         * Primera línea
         * Segunda línea
         *
         * @return algo
         */
        public String test() {
            return "x";
        }
    }
    """

    methods = extract_methods_from_source(source)
    method = methods[0]

    assert "Primera línea" in method.javadoc.description
    assert "Segunda línea" in method.javadoc.description


def test_method_with_annotation():
    source = """
    public class Test {
        @Override
        public String toString() {
            return "Test";
        }
    }
    """

    methods = extract_methods_from_source(source)

    assert len(methods) == 1
    assert methods[0].method_name == "toString"