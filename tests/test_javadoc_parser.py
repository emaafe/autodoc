from analyzer.java_extractor import extract_methods_from_source


def test_parse_basic_tags():
    source = """
    public class Test {
        /**
         * Hace algo
         * @param x valor
         * @return resultado
         */
        public int test(int x) {
            return x;
        }
    }
    """

    methods = extract_methods_from_source(source)
    jd = methods[0].javadoc

    assert jd.description == "Hace algo"
    assert jd.return_value == "resultado"
    assert len(jd.params) == 1
    assert jd.params[0].name == "x"


def test_parse_extended_tags():
    source = """
    public class Test {
        /**
         * Hace algo complejo
         * @param x valor
         * @return resultado
         * @example usoEjemplo
         * @ticket 1234
         * @notes nota importante
         */
        public int test(int x) {
            return x;
        }
    }
    """

    methods = extract_methods_from_source(source)
    jd = methods[0].javadoc

    assert jd.extra_tags["example"] == "usoEjemplo"
    assert jd.extra_tags["ticket"] == "1234"
    assert jd.extra_tags["notes"] == "nota importante"


def test_multiline_tags():
    source = """
    public class Test {
        /**
         * Descripción
         * @example linea1
         * linea2
         */
        public void test() {}
    }
    """

    methods = extract_methods_from_source(source)
    jd = methods[0].javadoc

    assert "linea1" in jd.extra_tags["example"]
    assert "linea2" in jd.extra_tags["example"]