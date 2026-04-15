from analyzer.java_extractor import extract_methods_from_source
from analyzer.normalizer import normalize_methods


def test_normalizer_basic_structure():
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
    normalized = normalize_methods(methods)

    m = normalized[0]

    assert "javadoc" in m
    assert m["javadoc"]["description"] == "Hace algo"
    assert len(m["javadoc"]["params"]) == 1


def test_normalizer_extended_tags():
    source = """
    public class Test {
        /**
         * Desc
         * @example ejemplo
         * @ticket 999
         */
        public void test() {}
    }
    """

    methods = extract_methods_from_source(source)
    normalized = normalize_methods(methods)

    jd = normalized[0]["javadoc"]

    assert "example" in jd
    assert "ticket" in jd
    assert jd["example"] == "ejemplo"
    assert jd["ticket"] == "999"