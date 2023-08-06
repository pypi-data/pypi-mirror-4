import logging
from xmlrpclib import ServerProxy, Fault, ProtocolError
from xml.parsers.expat import ExpatError

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


logger = logging.getLogger("everlytic-api")


try:
    EVERLYTIC_HOST = settings.EVERLYTIC['URL']
    EVERLYTIC_API_KEY = settings.EVERLYTIC['API_KEY']
    EVERLYTIC_LIST_ID = settings.EVERLYTIC['LIST_ID']
except AttributeError:
    raise ImproperlyConfigured("EVERLYTIC settings are missing")
except KeyError as e:
    raise ImproperlyConfigured("EVERLYTIC setting %s is missing." % str(e))


def subscribeUser(last_name, first_name,
                  email, receive_email,
                  everlytic_id=None):
    """ Subscribe the user to the everlytic mailing list, and return the
    everlytic user id to the caller.
    """
    # create the connection to the host
    sp = None
    try:
        sp = ServerProxy(EVERLYTIC_HOST)
    except IOError:
        logger.error("xmlrpclib: Could not connect to the remote host.")
        return None

    # Check for an existing everlytic user just to be safe, even if we
    # create her on our side for the first time. She may have subscribed
    # via other channels with Everlytic already.
    if not everlytic_id:
        everlytic_id = _checkForExistingEverlyticUser(sp, last_name,
                                                      first_name,
                                                      email)
        if not everlytic_id:
            # We have a new Everlytic user, so create the user on the everlytic
            # database, and set the subscriptions status accordingly
            return _createEverlyticUser(sp, email, receive_email,
                                        last_name, first_name)

    # For an existing user, update her status on the list
    _updateSubscription(sp, everlytic_id, receive_email)
    return everlytic_id


def _updateSubscription(sp, contact_id, receive_email):
    """ Update the subscription status of a contact on a mailing list.
    """
    try:
        result = sp.contacts.updateSubscriptions(EVERLYTIC_API_KEY,
                                                 contact_id,
                                                 {
                                                     str(EVERLYTIC_LIST_ID): {
                                                         "cmapping_email_status": receive_email and "subscribed" or "unsubscribed"
                                                     }
                                                 })
        if result['status'] != 'success':
            logger.warning("Everlytic error: %s", result['message'])
    except Fault as e:
        logger.error("XMLRPC Fault. Code: %s, Message %s", e.faultCode, e.faultString)
    except ProtocolError as e:
        logger.error("XMLRPC Protocol Error. url: %s, code: %s, message: %s", 
                e.url, e.errcode, e.errmsg)
    except ExpatError:
        logger.error("ExpatError: Response does not contain XML")


def _createEverlyticUser(sp, email, receive_email,
                         last_name=None, first_name=None):
    """ Create a new user on the EverLytic service and (un)subscribe them to
    the list, all in one go.
    """
    params = {'contact_email': email}
    if first_name is not None:
        params['contact_name'] = first_name
    if last_name is not None:
        params['contact_lastname'] = last_name
    try:
        result = sp.contacts.create(EVERLYTIC_API_KEY,
                                    params,
                                    [EVERLYTIC_LIST_ID],
                                    receive_email and "subscribed" or "unsubscribed",
                                    "update")
        if result['status'] == 'success':
            return result['contact_id']
        else:
            logger.warning("Everlytic error: %s", result['message'])
    except Fault as e:
        logger.error("XMLRPC Fault. Code: %s, Message %s", e.faultCode, e.faultString)
    except ProtocolError as e:
        logger.error("XMLRPC Protocol Error. url: %s, code: %s, message: %s", 
                e.url, e.errcode, e.errmsg)
    except ExpatError:
        logger.error("ExpatError: Response does not contain XML")

    return None


def _checkForExistingEverlyticUser(sp, last_name, first_name, email):
    """ Check if the user exists on the Everlytic database
    """
    try:
        # see if the user exists on the EverLytic service
        result = sp.contacts.getBatch(EVERLYTIC_API_KEY, {
            'contact_lastname': last_name,
            'contact_name': first_name,
            'contact_email': email
        })
        if int(result['total']) > 0:
            # TODO: Make sure this compromise will work!
            # Take the first result in the returned list
            everlytic_user = result['data'][0]
            return everlytic_user['contact_id']
    except Fault as e:
        logger.error("XMLRPC Fault. Code: %s, Message %s", e.faultCode, e.faultString)
    except ProtocolError as e:
        logger.error("XMLRPC Protocol Error. url: %s, code: %s, message: %s", 
                e.url, e.errcode, e.errmsg)
    except ExpatError:
        logger.error("ExpatError: Response does not contain XML")

    return None


def deleteEverlyticUser(contact_id):
    """ Delete the given contact from the Everlytic database
    """
    # Create the connection to the host
    sp = None
    try:
        sp = ServerProxy(EVERLYTIC_HOST)
    except IOError:
        logger.error("xmlrpclib: Could not connect to the remote host.")
        return

    # Delete the user
    try:
        result = sp.contacts.delete(EVERLYTIC_API_KEY, contact_id)
        if result['status'] != 'success':
            logger.warning("Everlytic error: %s", result['message'])
    except Fault as e:
        logger.error("XMLRPC Fault. Code: %s, Message %s", e.faultCode, e.faultString)
    except ProtocolError as e:
        logger.error("XMLRPC Protocol Error. url: %s, code: %s, message: %s", 
                e.url, e.errcode, e.errmsg)
    except ExpatError:
        logger.error("ExpatError: Response does not contain XML")
