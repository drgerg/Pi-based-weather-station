#!/usr/bin/env python3

import time,os,logging,configparser,argparse,traceback,signal,sys



#
## - - - - - TEST CODE BELOW HERE - - - -
#
#  Last time I checked, these were the systemctl .service files I've written.
#  They are located in /lib/systemd/system/ on these Raspbian OS Pi's around here.
#     allApp.service - Runs Flask/Gunicorn on this machine to serve as a single screen touching all the Pi's.
#     allPWS.service - Pulls weather data from mySQL, formats it and sends it to PWSWeather.com for display.
#
def main():
    result = []
    svcList = ['allApp.service','allPWS.service']
    for item in svcList:
        status = os.system('systemctl is-active --quiet ' + item)
        if status == 0:
            strStat = 'OK'
        else:
            strStat = 'NOT OK'
        ret = '{:>14s} {:<22s}'.format(strStat + ' :', item)
        bLen = str(len(svcList))
        print(ret)
        #logger.info(ret)
        result.append(ret)
    #logger.info(' End of Report ')
    return bLen,result
## - - - - - - END TEST CODE - - - - - - - 
#

def SignalHandler(signal, frame):
    if signal == 2:
        sigStr = 'CTRL-C'
        logger.info('* * * ' + sigStr + ' caught. * * * ')
    print("SignalHandler invoked")
    logger.info("Shutting down gracefully")
    logger.debug("Wrote to log in SignalHandler")
    logger.info("That's all folks.  Goodbye")
    logger.info(" - - - - z-RunTest.py DATA LOGGING STOPPED INTENTIONALLY - - - - ")
    sys.exit(0)

if __name__ == "__main__":

    parserTest = argparse.ArgumentParser()
    group = parserTest.add_mutually_exclusive_group()
    group.add_argument('-d', '--debug', help="Turn on debugging output to log file.", action="store_true")
    group.add_argument('-f', '--func', help="Call the specified function.", action="store")
    TestHome = os.getcwd()                              ## os.getcwd() give you the Current Working Directory.  If you run this from some other directory
    print(TestHome)                                     ## then the test.log file (for example) gets written there, not in the directory where this 
    logger = logging.getLogger(__name__)                ## python file lives.  
    #
    config = configparser.RawConfigParser()
    config.read(TestHome + '/allApp.conf')
    #
    argsTest = parserTest.parse_args()

    if argsTest.func:
        Tfunc = argsTest.func
        print(Tfunc)

    if argsTest.debug:
        logging.basicConfig(filename=TestHome + '/test.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=TestHome + '/test.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - z-sysRunTest.py DATA LOGGING STARTED - - - - ")
    print('Logger info')
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
#        while True:
#            main()
        main()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - a-sysRunTest.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")