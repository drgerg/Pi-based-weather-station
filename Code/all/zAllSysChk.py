#!/usr/bin/env python3

import time,os,logging,configparser,argparse,traceback,signal,sys,subprocess,io,reporter
from time import sleep

#
## - - - - - TEST CODE BELOW HERE - - - -
#

def main():
    config = configparser.ConfigParser()
    config.read(ZASCHome + '/zAllSysChk.conf')
    result = []
    sysList = []
    inc = 1
    while 'sys' + str(inc) in config['Systems']:
        sysVar = config.get('Systems','sys' + str(inc))
        portVar = config.get('Systems','port' + str(inc))
        pingRes = subprocess.call(['/bin/ping', '-c', '1', sysVar], stdout=subprocess.DEVNULL)
        logger.debug('Ping for ' + sysVar + ' returned: ' + str(pingRes))
        if pingRes == 0:                                        # We are connected.  Move ahead.  If not, don't do any of this stuff.
            inc2 = 1
            while 'service' + str(inc2) in config[sysVar]:
                svcVar = config.get(sysVar,'service' + str(inc2))
                status = os.system('ssh -p ' + portVar + ' ' + sysVar + ' ' + 'systemctl is-active --quiet ' + svcVar)
                if status == 0:
                    strStat = 'OK'
                else:
                    strStat = 'NOT OK'
                result.append(sysVar + ',' + svcVar + ',' + strStat)
                inc2 += 1
            inc += 1
        else:                                                           # We are NOT CONNECTED.
            logger.info('Ping test for ' + sysVar +' failed.')
            strStat = 'BAD PING'
            svcVar = 'ping test'
            result.append(sysVar + ',' + svcVar + ',' + strStat)
            inc += 1
    else:
        # print(result)
        for row in result:
            if 'NOT OK' in row or 'BAD PING' in row:
                reporter.msgS('zAllSysChk Report',str(row))
                logger.info(str(row))
            else:
                pass
        # print("That's all.")
    return result
        
 
#
## - - - - - - END TEST CODE - - - - - - - 
#


def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info(' * * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - zAllSysChk.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":

    ZASCparser = argparse.ArgumentParser()
    ZASCparser.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
    ZASCparser.add_argument('-f', '--func', help="Call the specified function.", action="store")
    ZASCHome = os.getcwd()                              ## os.getcwd() give you the Current Working Directory.  If you run this from some other directory
    # print(ZASCHome)                                     ## then the test.log file (for example) gets written there, not in the directory where this 
    logger = logging.getLogger(__name__)                ## python file lives.  
    #

    #
    argsTest = ZASCparser.parse_args()

    # if argsTest.func:
    #     Tfunc = argsTest.func
    #     print(Tfunc)

    if argsTest.debug:
        logging.basicConfig(filename=ZASCHome + '/zAllSysChk.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=ZASCHome + '/zAllSysChk.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - zAllSysChk.py DATA LOGGING STARTED - - - - ")
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
        while True:
            main()
            sleep(600)
            # logger.info('main() looped.')
        # main()
        # pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - zAllSysChk.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")
