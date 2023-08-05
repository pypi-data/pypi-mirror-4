# -*- coding: utf-8 -*-
"""The @@jvzoo view that handles JVZoo purchase notifications."""

from five import grok
from niteoweb.ipn.core.interfaces import IIPN
from niteoweb.ipn.jvzoo.interfaces import SecretKeyNotSet
from niteoweb.ipn.jvzoo.interfaces import UnknownTransactionType
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getAdapter

import transaction
import hashlib
import logging

logger = logging.getLogger("niteoweb.ipn.jvzoo")


class JVZoo(grok.View):
    """A view for handling IPN POST requests from JVZOO."""

    grok.context(ISiteRoot)
    grok.require('zope2.View')

    TYPES_TO_ACTIONS = {
        'SALE': 'enable_member',
        'BILL': 'enable_member',
        'RFND': 'disable_member',
        'CGBK': 'disable_member',
        'INSF': 'disable_member',
        'CANCEL-REBILL': 'disable_member',
        'UNCANCEL-REBILL': 'enable_member',
    }
    """Mapping from JVZoo Transaction Types to niteoweb.ipn.core actions."""

    def render(self):
        """Handler for JVZoo IPN POST requests."""
        # check for POST request
        if not self.request.form:
            msg = 'No POST request.'
            logger.warning(msg)
            return msg

        # prepare values
        params = dict(self.request.form)
        params['secretkey'] = api.portal.get_registry_record(
            'niteoweb.ipn.jvzoo.interfaces.IJVZooSettings.secretkey')

        try:
            # verify and parse post
            self._verify_POST(params)
            data = self._parse_POST(params)
            logger.info("POST successfully parsed for '%s'." % data['email'])

            # call appropriate action in niteoweb.ipn.core
            ipn = getAdapter(self.context, IIPN)
            trans_type = data['trans_type']
            if trans_type in self.TYPES_TO_ACTIONS:
                action = self.TYPES_TO_ACTIONS[trans_type]
                logger.info("Calling '%s' in niteoweb.ipn.core." % action)
                params = {
                    'email': data['email'],
                    'product_id': data['product_id'],
                    'trans_type': data['trans_type'],
                    'fullname': data.get('fullname'),    # optional
                    'affiliate': data.get('affiliate'),  # optional
                }
                getattr(ipn, action)(**params)
            else:
                raise UnknownTransactionType(
                    "Unknown Transaction Type '%s'." % trans_type)

        except KeyError as ex:
            msg = "POST parameter missing: %s" % ex
            logger.warning(msg)
            transaction.abort()
            return msg

        except AssertionError:
            msg = "Checksum verification failed."
            logger.warning(msg)
            transaction.abort()
            return msg

        except Exception as ex:
            msg = "POST handling failed: %s" % ex
            logger.warning(msg)
            transaction.abort()
            return msg

        return 'Done.'

    def _verify_POST(self, params):
        """Verifies if received POST is a valid JVZoo POST request.

        :param params: POST parameters sent by JVZoo Notification Service
        :type params: dict

        """
        if not params['secretkey']:
            raise SecretKeyNotSet('JVZoo secret-key is not set.')
        strparams = ""
        for key in iter(sorted(params.iterkeys())):
            if key in ['cverify', 'secretkey']:
                continue
            strparams += params[key] + "|"
        strparams += params['secretkey']
        sha = hashlib.sha1(strparams.encode('utf-8')).hexdigest().upper()
        assert params['cverify'] == sha[:8], 'Checksum verification failed.'

    def _parse_POST(self, params):
        """Parse POST from JVZoo and extract information we need.

        :param params: POST parameters sent by JVZoo Notification Service
        :type params: dict

        """
        return {
            'email': params['ccustemail'],
            'fullname': u"%s" % params['ccustname'].decode("utf-8"),
            'product_id': params['cproditem'],
            'affiliate': params['ctransaffiliate'],
            'trans_type': params['ctransaction'],
        }
