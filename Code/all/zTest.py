#!/usr/bin/env python3

# import time,os,logging,argparse,traceback,signal,sys,subprocess,io
import time,os,logging,configparser,argparse,traceback,signal,sys,subprocess,io


#
## - - - - - TEST CODE BELOW HERE - - - -
#
def remPinChk():
    TestHome = os.getcwd()
    config = configparser.ConfigParser()
    config.read(TestHome + '/zAllSysChk.conf')
    sysVar = config.get('Systems','sys' + '1')
    portVar = config.get('Systems','port' + '1')
    pathVar = config.get('Systems','path' + '1')
    DoorStat = 'Unknown'
    bpStat = 'Unknown'
    status = subprocess.check_output(['ssh','-p',portVar,sysVar,pathVar+'ohdpinchk.py'])
    status = status.decode()
    status = status.splitlines()
    DoorStat = status[0]
    bpStat = status[1]
    gCPU = status[2]
    return DoorStat,bpStat,gCPU

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
    # print(TestHome)                                     ## then the test.log file (for example) gets written there, not in the directory where this 
    logger = logging.getLogger(__name__)                ## python file lives.  
    #
    # config = configparser.RawConfigParser()
    # config.read(TestHome + '/allApp.conf')
    #
    argsTest = parserTest.parse_args()

    # if argsTest.func:
    #     Tfunc = argsTest.func
    #     print(Tfunc)

    if argsTest.debug:
        logging.basicConfig(filename=TestHome + '/zTest.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=TestHome + '/zTest.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - zTest.py DATA LOGGING STARTED - - - - ")
    # print('Logger info')
    #
    signal.signal(signal.SIGINT, SignalHandler)  ## This one catches CTRL-C from the local keyboard
    signal.signal(signal.SIGTERM, SignalHandler) ## This one catches the Terminate signal from the system    
    try:
#        print(" Top of try")
#        while True:
#            main()
        remPinChk()
        pass
#                print("Bottom of try")
    except Exception:
        logger.info("Exception caught at bottom of try.", exc_info=True)
        error = traceback.print_exc()
        logger.info(error)
        logger.info("That's all folks.  Goodbye")
        logger.info(" - - - - zTest.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")