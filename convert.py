import sqlite3,datetime,re,os,sys,getopt
import email
import errno
import mimetypes
import smtplib
import email.generator
from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Message import Message
from email.MIMEAudio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from optparse import OptionParser
from types import IntType
from types import StringTypes

def main(argv):
        nome = ''
        try:
                opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
        except getopt.GetoptError:
                print 'convert.py -i <filename>.imm'
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print 'convert.py -i <inputfile>.imm'
                        sys.exit()

        conn = sqlite3.connect('Containers.db')
        c = conn.cursor()
        ca = conn.cursor()
        Consulta = conn

        cons = Consulta.execute("Select ContainerID from Containers where FileName ='"+nome+"'").fetchall()

        if len (cons)==0:
                print "File or table not found "+nome
                exit()
        else:
                for caa in cons:
                        cid=caa[0]

        dirsaida='./recovered/'+nome
        try:
                os.stat(dirsaida)
        except:
                os.mkdir(dirsaida)

        consulta="Select HeaderID, FromSender,ToSender,MsgPos,MsgSize,ReceivedDate,Subject from Headers where ContainerID  like'"+cid+"' and Deleted = 0 ;"
        nom=nome+'.imm'
        f = open(nom)
        cnt=0
        for s in c.execute(consulta):
                header= s[0] #HeaderID
                fromsender= s[1] #FromSender
                tosender = 'Delivered-To:'+s[2] #ToSender
                msgpos = s[3] #MsgPos
                msgsize = s[4] #MsgSize
                rec='Received: by 10.0.0.1 with SMTP id 123123aa'
                v=datetime.datetime.fromtimestamp(s[5]) #ReceivedDate ja convertido
                con = "select Path from Attachments where HeaderID = '"+header+"';"
                
                f.seek(msgpos)
                data=f.read(msgsize)
                filename = nome+'-part-%03d%s' % (cnt, '.eml')
                fp = open(os.path.join('./tmp', filename), 'w')
                fp.write(tosender.encode('utf8'))
                fp.write('\n')
                fp.write(data)
                fp.close()
                d = open(os.path.join('./tmp', filename))
                cnt+=1
                msg = email.message_from_file(d)
                
                for anexos in ca.execute(con):
                        an=anexos[0].replace("\\","/")
                        if os.path.isfile(os.path.join('./Attachments',an.encode('utf8'))):
                                path = os.path.join('./Attachments',an.encode('utf8'))
                                ctype, encoding = mimetypes.guess_type(path)
                                if ctype is None or encoding is not None:
                                        ctype = 'application/octet-stream'
                                maintype, subtype = ctype.split('/', 1)
                                fp = open(path, 'rb')
                                print ctype
                                if subtype == 'text':
                                        part = MIMEText(fp.read(), _subtype=subtype)
                                elif subtype == 'image':
                                        part = MIMEImage(fp.read(), _subtype=subtype)
                                elif subtype == 'audio':
                                        part = MIMEAudio(fp.read(), _subtype=subtype)
                                else:
                                        part = MIMEBase(maintype, subtype)
                                        part.set_payload(fp.read())
                                        Encoders.encode_base64(part)
                                fp.close()
                                nan1="recuperado-"+an.encode('utf8')
                                part.add_header('Content-Disposition', 'attachment;filename=\"'+nan1+'\"')
                                try:
                                        msg.attach(part)
                                        print subtype
                                except Exception, e:
                                        #print part
                                        print header+" "+nan1.decode('utf8')
                                        print maintype+' '+ctype
                                        print e
                                        continue
                d.close()
                dirsaida='./recovered/'+nome
                saida = open(os.path.join(dirsaida, filename), 'w')
                generator = email.generator.Generator(saida)
                generator.flatten(msg)

if __name__ == "__main__":
   main(sys.argv[1:])
