#!/usr/bin/env python3
import socket,os,sys,traceback,logging,signal,configparser,pickle
from time import sleep

## Init area.  configparser and logger
#
SockHome = os.path.abspath(os.path.dirname(__file__))
config = configparser.RawConfigParser()
config.read(SockHome + '/Sock.conf')
logger = logging.getLogger(__name__)

def main():
    HOST = '192.168.1.15'                                           # We're using Unix sockets to send this data.
    PORT = 64444                                                    # Choose a weird port way high in the ports range.
    InCmd = argssm.mode                                             # Save commandline argument to a variable.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # Setup a stream IP socket. I think this uses TCP
            s.connect((HOST, PORT))                                     # Connect to the remote machine.
            sockXferIn = pickle.dumps(InCmd)
            sleep(1)                                                # Hold up a sec.
            s.sendall(sockXferIn)                                   # Send the command to start the data-gathering on the other end.
            sleep(2)
            s.close()
            print('Sent "' + str(InCmd) + '" and Closed.')
            logger.info('Sent "' + InCmd + '" to ' + str(HOST))
    except socket.error as err:
            print('There was an error:' + str(err))
            logger.info('There was an error: ' + str(err))
            sys.exit(1)
            pass

def getShopPins():
    HOST = '192.168.1.15'                                           # We're using Unix sockets to send this data.
    PORT = 64444                                                    # Choose a weird port way high in the ports range.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ps:
            ps.connect((HOST, PORT))
            sockReq = (pickle.dumps('sendPins'))
            sleep(1)
            ps.sendall(sockReq)
            sleep(2)
            print('Request for Pins sent.')
            logger.info('Request for Pins sent to shop.')
            shopTpins = ps.recv(2048)
            with open('shopCurrentPins.pkl', 'wb') as inFile:
                inFile.write(shopTpins)
            sleep(2)
            inFile.close()
            ps.close()
    except socket.error as err:
            print('There was an error:' + str(err))
            logger.info('There was an error: ' + str(err))
            sys.exit(1)
            pass

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
            parsersm.add_argument("-m", "--mode", type=str, help="System mode. Valid options are: cool, off.")
            argssm = parsersm.parse_args()
            if argssm.debug:
                logging.basicConfig(filename=SockHome + '/sock.log', format='[%(name)s]:%(levelname)s: %(message)s. - %(asctime)s', datefmt='%D %H:%M:%S', level=logging.DEBUG)
                logging.info("Debugging output enabled")
            else:
                logging.basicConfig(filename=SockHome + '/sock.log', format='%(asctime)s - %(message)s.', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.INFO)
            #
            ## End Command line arguments parsing

            signal.signal(signal.SIGINT, SignalHandler)
            logger.debug("Top of try")
            main()
            logger.info("Bottom of try")

        except  ValueError as errVal:
            print(errVal)
            sys.exit(1)
        logger.info("That's all folks.  Goodbye")


