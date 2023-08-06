pair_fail_msg = ("Testing function {0}\n\n"
                "In:\n"
                " {1!r}\n"
                "Expected:\n"
                " {2!r}\n"
                "Got:\n"
                " {3!r}\n")
def check_func(func, pairs):
    """Utility function for the common case of checking a function with a
    sequence of input/output pairs.
    
    Parameters
    ----------
    func : callable
      The function to be tested. Should accept a single argument.
    pairs : iterable
      A list of (*input, expected_output) tuples.
    
    Returns
    -------
    None. Raises an AssertionError if any output does not match the expected
    value.
    """
    for *inp, expected in pairs:
        out = func(*inp)
        assert out == expected, \
                        pair_fail_msg.format(func.__name__, inp, expected, out)
