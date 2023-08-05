from operator import eq

class Matcher(object):
    """For use in mocking, allows comparison of objects via some
    arbitrary function called compare,

    see http://www.voidspace.org.uk/python/mock/examples.html#more-complex-argument-matching
    """
    def __init__(self, compare, some_obj):
        self.compare = compare
        self.some_obj = some_obj

    def __eq__(self, other):
        if self.compare(self.some_obj, other):
            return True
        raise AssertionError("{0} is not equal to {1}".format(
            self.some_obj, other))

class SubDictMatches(Matcher):

    def __init__(self, expected):
        super(SubDictMatches, self).__init__(assert_in_dicts, expected)

def assert_in_dicts(expected, actual, comp_func=eq):
    """Checks that all the key value pairs in expected are in a dictionary
    in actual, which is a template context
    """
    for key, value in expected.items():
        if key not in actual:
            raise AssertionError("Actual does not contain key {0}".format(
                key))
        actual_value = actual.get(key)
        if not comp_func(actual_value, value):
            raise AssertionError("Values for key '{0}' don't match, expected "
                                 "value was {1}, value in actual was {2}".
                                 format(key, value, actual_value))
    return True

def make_dict_assert_func(comp_func):
    """Creates an assertion cuntions which compares values in two
    dictionaries using comp_func
    """
    def assert_func(dictionary, context):
        return assert_in_dicts(dictionary, context, comp_func=comp_func)
    return assert_func

def compare_urls(url1, url2):
    """Compares urls for equality without respect to the order of
    GET parameters
    """
    pr1 = urlparse.urlparse(url1)
    pr2 = urlparse.urlparse(url2)
    query1 = urlparse.parse_qs(pr1.query)
    query2 = urlparse.parse_qs(pr2.query)
    result = True
    for key in ["scheme", "netloc", "hostname", "port", "path"]:
        if getattr(pr1, key) != getattr(pr2, key):
            raise AssertionError("url {0} did not match {1}".format(url1, url2))
    if query1 != query2:
        raise AssertionError("GET parameters for {0} and {1} "
                             "did not match".format(url1, url2))
    return result

