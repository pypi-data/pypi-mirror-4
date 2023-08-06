import z3c.recipe.compattest.testing


def test_suite():
    return z3c.recipe.compattest.testing.DocFileSuite(
        'README.txt', 'runner.txt')
