#!/usr/bin/env python3

""" reporter.py - a re-use of ohdsendmail.py from the ohd (OverHead Door) project.  Email pre-configured messages.
    2020 - Gregory Allen Sanders (Github - casspop)"""

import os
import sys
import configparser
import logging
import time
import signal
#
## ConfigParser init area.  Get some info out of working.conf.
#
ohdHome = os.getcwd()
config = configparser.RawConfigParser()
config.read(ohdHome + '/reporter.conf')
#
## End ConfigParser init

logger = logging.getLogger(__name__)

logger.debug("Sending Message")


def main():
    logger.debug("Started the main() function")
    tMsg = "This message comes to you because you ran reporter.py from the commandline, and it is not currently setup to actually do anything when used that way."
    tSub = "Reporter.py and the need for configuration."
    msgS(tSub, tMsg)
    logger.debug("Finished the Main() function")


def msgS(tSub, tMsg):
    logger.debug("Started msgS() function")
    x = int(config.get('Notify', 'NotifyNumber'))
    tNow = time.strftime("%H:%M:%S", time.localtime())
    for i in range(1, x+1):
        Email = config.get('Notify', 'NotifyEmail' + str(i))
        os.system("echo " + tMsg + " at " + tNow + " | mail -s " + "\'" + tSub + "\' " + Email)
    logger.info("'" + tMsg + "' Message Sent")
    logger.debug("Finished the msgS() function")


def SignalHandler(signal, frame):
        logger.info("Cleaning up . . . \n = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
        logger.info("Shutting down gracefully")
        logger.debug("This is SignalHandler")
        logger.info("Displayed .info and .debug in SignalHandler")
        logger.info("Shutdown initiated")
        logger.debug("Wrote to log in SignalHandler")
        sys.exit(0)


if __name__ == "__main__":
        try:
            import argparse

            ## Command line arguments parsing
            #
            parsersm = argparse.ArgumentParser()
            parsersm.add_argument("-d", "--debug", help="Turn on debugging output to stderr", action="store_true")
            argssm = parsersm.parse_args()
            if argssm.debug:
                logging.basicConfig(filename=ohdHome + '/reporter.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=ohdHome + '/reporter.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing

            signal.signal(signal.SIGINT, SignalHandler)
            logger.debug("Top of try")
            main()
            logger.info("Bottom of try")

        except:
            pass
            logger.info("That's all folks.  Goodbye")

