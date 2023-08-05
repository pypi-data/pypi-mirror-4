from daybed.tests.support import BaseWebTest


class FunctionaTest(BaseWebTest):

    def test_spore(self):
        # the spore resource should just work.
        self.app.get('/spore')
