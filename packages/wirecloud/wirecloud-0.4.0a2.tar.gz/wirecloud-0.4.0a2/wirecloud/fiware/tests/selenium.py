from wirecloud.commons.test import WirecloudSeleniumTestCase


__test__ = False


class FiWareSeleniumTestCase(WirecloudSeleniumTestCase):

    def test_add_fiware_marketplace(self):

        self.login()

        self.add_marketplace('fiware', 'http://localhost:8080', 'fiware')

    def test_delete_fiware_marketplace(self):

        self.login()

        self.add_marketplace('fiware', 'http://localhost:8080', 'fiware')
        self.delete_marketplace('fiware')
