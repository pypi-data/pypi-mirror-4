
import optparse,sys

from sms import truncate
from modem import GSMModemReader, ATError

def log_data(field,data):
    print "++ %s: %s" % (field,data)

def print_sms_list(sms):
    print u"%3s| %-19s | %-13s | %s" % ("Msg","Date","Number","Message")
    print u"-" * 79
    for sms in sorted(sms,lambda x,y: cmp(x.TS,y.TS)):
        print u"%3d| %-19s | %-13s | %s" % \
            (sms.index, sms.TS, sms.OAnumber, truncate(sms.decoded,36))

def run():

    parser = optparse.OptionParser()

    parser.add_option("-d","--device")
    parser.add_option("--id",action="store_true")
    parser.add_option("--list",action="store_true")
    parser.add_option("--get",action="store",type="int")
    parser.add_option("--send",action="store")
    parser.add_option("--dump",action="store",type="int")
    parser.add_option("--delete",action="store",type="int")
    parser.add_option("--interact",action="store_true")
    parser.add_option("--debug",action="store_const",const=log_data)

    options, args = parser.parse_args()

    try:
        if options.device:
            try:
                modem = GSMModemReader(options.device)
            except OSError,e:
                print "Error opening device %s: %s" % (options.device,e)
                sys.exit()
        else:
            print "ERROR: Must specify device\n"
            parser.print_help()
            sys.exit()
            
        try:
            if options.id:
                print "Device:", modem.getModel()
                print "MSISDN:", modem.getMSISDN()
                print "IMSI:", modem.getIMSI()
                print "IMEI:", modem.getIMEI()
            elif options.get:
                sms = modem.getSMS(options.get,options.debug)
                if sms:
                    print
                    print u"Message:  %d" % options.get
                    print u"From:     %s" % sms.OAnumber 
                    print u"Sent:     %s" % sms.TS 
                    print u"Message:  %s" % sms.decoded
                    print
                else:
                    print "Message %d not found" % options.get
            elif options.delete:
                print modem.deleteSMS(options.delete)
            elif options.send:
                if sys.stdin.isatty():
                    msg = raw_input("Message: ")
                else:
                    msg = sys.stdin.read().strip()
                modem.sendSMS(options.send,msg)
            elif options.list:
                sms = modem.getSMSList()
                print_sms_list(sms)
            elif options.dump:
                sms = modem.getSMS(options.dump,options.debug)
                sms.dump()
            elif options.interact:
                modem.readlines()
                modem.interact()
            else:
                parser.print_help()
        except KeyboardInterrupt:
            print "[Closing Connection]"
            pass
    except ATError, e:
        print "ERROR: AT Command Failed"
        print e

if __name__ == '__main__':
    run()

