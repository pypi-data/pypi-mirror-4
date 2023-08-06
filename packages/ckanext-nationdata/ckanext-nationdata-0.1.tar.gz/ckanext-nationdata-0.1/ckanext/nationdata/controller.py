import sys
from ckan.lib.base import request
from ckan.lib.base import c, g, h
from ckan.lib.base import model
from ckan.lib.base import render
from ckan.lib.base import _

from ckan.lib.navl.validators import not_empty

from ckan.controllers.home import HomeController


class CustomPageController(UserController):
    """This controller is used to extend some of the static pages with
    the accompanying URL routing associated with it."""
    def developers(self):
        return render('home/developers.html')

