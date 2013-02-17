__author__ = 'dur'
import logging

NAME = "PeriodicPassExchange: "
timer = 0
RES_MODULE = "PASS_EXCH_RES:"
NEW_PASS = "NEW_PASS"

def execute(paramsDictionary, message):
	global timer
	if timer == 0:
		timer = int(paramsDictionary["CONFIG_PARAMS"]["passExchangePeriod"])
		logging.error(NAME + "Wysylam zapytanie o stare haslo")
		paramsDictionary["SOCKET"].send_message(RES_MODULE+NEW_PASS)
	else:
		timer = timer -1