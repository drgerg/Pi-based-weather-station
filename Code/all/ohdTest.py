#!/usr/bin/env python3

# import time,os,logging,argparse,traceback,signal,sys,subprocess,io
import time,os,logging,configparser,argparse,traceback,signal,sys,subprocess,io,socket,pickle
from time import sleep
#
## - - - - - TEST CODE BELOW HERE - - - -
#
def remPinChk():
    HOST = '192.168.1.14'                                           # We're using Unix sockets to send this data.
    PORT = 64444                                                    # Choose a weird port way high in the ports range.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # Setup a stream IP socket. I think this uses TCP
            s.connect((HOST, PORT))                                     # Connect to the remote machine.
            toHost = (pickle.dumps('pincheck'))
            # sleep(1)                                                # Hold up a sec.
            s.sendall(toHost)                                   # Send the command to start the data-gathering on the other end.
            # sleep(2)
            print('Sent doorpi a pincheck request: ')
            ohdPnChk = s.recv(2048)
            rcvFrmHost = pickle.loads(ohdPnChk)
            print(str(rcvFrmHost))
            DoorStat = rcvFrmHost[0]
            bpStat = rcvFrmHost[1]
            gCPU = rcvFrmHost[2]
            s.close()
    except socket.error as err:
            print('There was an error:' + str(err))
            sys.exit(1)
            pass
    return DoorStat,bpStat,gCPU

def remSoftBypass(SBPcmd):
    SBPcmd = SBPcmd
    HOST = '192.168.1.14'                                           # We're using Unix sockets to send this data.
    PORT = 64444                                                    # Choose a weird port way high in the ports range.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # Setup a stream IP socket. I think this uses TCP
            s.connect((HOST, PORT))                                     # Connect to the remote machine.
            toHost = (pickle.dumps(SBPcmd))
            # sleep(1)                                                # Hold up a sec.
            s.sendall(toHost)                                   # Send the command to start the data-gathering on the other end.
            # sleep(2)
            print('Sent doorpi a ohd Soft Bypass request: ' + str(SBPcmd))
            SBPRtn = s.recv(2048)
            rcvFrmHost = pickle.loads(SBPRtn)
            print(str(rcvFrmHost))
            SBPRtn = rcvFrmHost
            s.close()
    except socket.error as err:
            print('There was an error:' + str(err))
            sys.exit(1)
            pass
    return SBPRtn

#
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
        logging.basicConfig(filename=TestHome + '/ohdTest.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
        logging.info("Debugging output enabled")
    else:
        logging.basicConfig(filename=TestHome + '/ohdTest.log', format='%(asctime)s - %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
    #
    logger.info(" - - - - ohdTest.py DATA LOGGING STARTED - - - - ")
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
        logger.info(" - - - - ohdTest.py DATA LOGGING STOPPED BY EXCEPTION - - - - ")

# def remPinChk():
#     TestHome = os.getcwd()
#     config = configparser.ConfigParser()
#     config.read(TestHome + '/zAllSysChk.conf')
#     sysVar = config.get('Systems','sys' + '1')
#     portVar = config.get('Systems','port' + '1')
#     pathVar = config.get('Systems','path' + '1')
#     DoorStat = 'Unknown'
#     bpStat = 'Unknown'
#     # status = subprocess.check_output(['ssh','-p',portVar,sysVar,pathVar+'ohdpinchk.py'])
#     status = subprocess.check_output(['ssh','-p','3155','doorpi','/home/greg/ohd/ohdpinchk.py'])
#     print(status)
#     status = status.decode()
#     status = status.splitlines()
#     print(status)
#     DoorStat = status[0]
#     bpStat = status[1]
#     gCPU = status[2]
#     return DoorStat,bpStat,gCPU