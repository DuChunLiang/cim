#!/usr/bin/env python

import udsoncan
from udsoncan.connections import IsoTPConnection
from udsoncan.client import Client
# from udsoncan.exceptions import *
from udsoncan.services import *
from . import uds_configs
import sys


def start():
    data = str(sys.argv[1]).encode(encoding="utf-8")
    conn = IsoTPConnection('can0', rxid=0x7e8, txid=0x7e0)
    config = uds_configs.default_client_config
    config['data_identifiers'][udsoncan.DataIdentifier.VIN] = '>%ss' % len(data)

    with Client(conn, request_timeout=2, config=config) as client:
        try:
            # client.change_session(DiagnosticSessionControl.Session.programmingSession)  # integer with value of 3
            # client.unlock_security_access(5)
            vin = client.write_data_by_identifier(udsoncan.DataIdentifier.VIN, data)
            print("send success", vin)
        except NegativeResponseException as e:
            print('Server refused our request for service %s with code "%s" (0x%02x)'
                  % (e.response.service.get_name(), e.response.code_name, e.response.code))
        except InvalidResponseException as e:
            print('Server sent an invalid payload : %s' % e.response.original_payload)


start()