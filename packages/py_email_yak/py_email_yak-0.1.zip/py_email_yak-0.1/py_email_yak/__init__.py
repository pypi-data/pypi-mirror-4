"""
.. module:: email_yak_python
.. moduleauthor:: Martin Charles <martincharles07@gmail.com>
.. _pushemaildoc: http://docs.emailyak.com/push-notifications.html
"""

import requests

BASE_URL = "https://api.emailyak.com/v1/"
HEADERS = {"Content-Type":"application/json"}

def raise_for_status_message(obj):
    try:
        obj.raise_for_status()
    except requests.exceptions.HTTPError:
        raise requests.exceptions.HTTPError (obj.json()["Message"])

def del_unused(dictionary):
    del_list = []
    for key, value in dictionary.items():
        if value is None:
            del_list.append(key)
    
    for i in del_list:
        del dictionary[i]
    
    return dictionary

class email_yak():
    """
    The main email-yak class which stores your API Key executes various functions.
    """
    def __init__ (self, api_key):
        """
        The init method for the email-yak class.
        
        :param api_key: The API key used to sign into email-yak and use it.
        :type api_key: str
        """
        self.auth_url = BASE_URL + api_key + "/json/"
    
    def register_domain(self, domain, callback_url = None, push_email = None):
        """
        This function registers a domain on the Email Yak service.
        
        :param domain: The domain to be registered.
        :type domain: str
        
        :param callback_url:  A POST request will be sent to the address provided with information about the email received. More information can be found `here <http://www.google.ch>`.
        :type callback_url: str
        
        :param push_email: If True email-yak will try to push the full contents of any received email to the callback URL, via HTTP POST.
        :type push_email: bool
        
        .. note:: Check `here <http://docs.emailyak.com/push-notifications.html>`_  for more information about the callback_url parameter.
        """
        dict_data = {
                     "Domain":domain,
                     "CallbackURL":callback_url,
                     "PushEmail":push_email
                     }
        dict_data = del_unused(dict_data)
        r = requests.post(
                                 self.auth_url + "register/domain/",
                                 headers = HEADERS,
                                 data = json.dumps(dict_data)
                                 )
        raise_for_status_message(r)
        
    def register_address(self, address, callback_url = None, push_email = None):
        """
        This function registers an email address on the Email Yak service.
        
        :param address: The email address to be registered.
        :type address: str
        
        :param callback_url:  A POST request will be sent to the address provided with information about the email received. More information can be found `here <http://www.google.ch>`.
        :type callback_url: str
        
        :param push_email: If True email-yak will try to push the full contents of any received email to the callback URL, via HTTP POST.
        :type push_email: bool
        
        .. note:: Check `here <http://docs.emailyak.com/push-notifications.html>`_  for more information about the callback_url parameter.
        .. note:: You can only use domains that are registered to emailyak. You can find out how to register domains `here <http://docs.emailyak.com/setup-your-domain.html>`_ or by running the :py:method:`register_domain`.
        """
        dict_data = {
                     "Address":address,
                     "CallbackURL":callback_url,
                     "PushEmail":push_email
                     }
        dict_data = del_unused(dict_data)
        r = requests.post(
                                 self.auth_url + "register/address/",
                                 headers = HEADERS,
                                 data = json.dumps(dict_data)
                                 )
        raise_for_status_message(r)