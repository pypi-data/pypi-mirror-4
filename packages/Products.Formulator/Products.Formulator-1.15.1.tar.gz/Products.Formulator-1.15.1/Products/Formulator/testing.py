

from infrae.wsgi.testing import BrowserLayer, TestRequest
import Products.Formulator


class FormulatorLayer(BrowserLayer):
    default_products = BrowserLayer.default_products + [
        'Formulator']
    default_users = {
        'manager': ['Manager'],
        }


FunctionalLayer = FormulatorLayer(
    Products.Formulator, zcml_file='configure.zcml')

__all__ = ['FunctionalLayer', 'TestRequest']
