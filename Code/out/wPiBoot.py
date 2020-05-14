#!/usr/bin/env python3
##
## When outMainDATA.py sees there are too many unanswered pings from the computer where the mySQL server runs, 
## it creates a file in the home directory called 'rebootItNow'.  This routine runs as a service, and looks for
## that file.  If it finds it, it deletes it and then reboots the Pi.  That normally resets things and restores 
## connectivity.
##
#   wPiBoot.py - cleanly reboot when loss of connectivity is discovered.

#     Copyright (c) 2019,2020 - Gregory Allen Sanders.

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import time,os,logging,configparser,argparse,traceback,signal,sys
from time import sleep

parserWPB = argparse.ArgumentParser()
group = parserWPB.add_mutually_exclusive_group()
group.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
group.add_argument('-f', '--func', help="Call the specified function.", action="store_true")
WPBHome = os.getcwd()
logger = logging.getLogger(__name__)
#
config = configparser.RawConfigParser()
config.read(WPBHome + '/out.conf')
#
argsWPB = parserWPB.parse_args()

if argsWPB.debug:
    logging.basicConfig(filename=WPBHome + '/outMain.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
    logging.info("Debugging output enabled")
else:
    logging.basicConfig(filename=WPBHome + '/outMain.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
#
logger.info(" - - - - WPBoot DATA LOGGING STARTED - - - - ")
logger.info("  INITIAL CONFIGURATION COMPLETE  ")
logger.info("'HOME' path is: " + WPBHome)

#
## - - - - - MAIN CODE BELOW HERE - - - -
#
def main():
    if os.path.isfile(WPBHome + '/rebootItNow'):
        os.remove(WPBHome + '/rebootItNow')
        if os.path.isfile(WPBHome + '/rebootItNow'):
            logger.info('Failed to remove reboot file.')
        else:
            logger.info('Found reboot file and deleted it.  Sending reboot command now.')
            os.system('reboot')
            pass
    else:
        pass
    sleep(2)
#
## - - - - - - END MAIN CODE - - - - - - - 
#

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - WPBoot DATA LOGGING STOPPED BY DESIGN - - - - ")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
        print(" Top of try")
        while True:
            main()
#        main()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - DATA LOGGING STOPPED BY EXCEPTION - - - - ")