import pdb
import csv
import vobject
import pypeople

file2 = 'Thunderbird_v1.csv'

contacts = []
with open(file2,'rb') as fh:
    spamreader = csv.reader(fh, delimiter=',', quotechar='|')
    for row in spamreader:
        header = row
        break
    for row in spamreader:
        z = {}
        for h,k in zip(header, row):
            z[h] = k
        contacts.append(z)


def dict_from_thunderbird_dict(tBirdDict):
    """ Converts a thunderbird dict into  a vObjectDict
    along with the nich for the filename it should be saved as
    @retrurn nick, vObjDict
    """
    nick = None
    vObjDict = {}
    if 'Display Name' in tBirdDict.keys() and tBirdDict['Display Name'] != '':
        nick = tBirdDict['Display Name']
    elif 'Nickname' in tBirdDict.keys() and tBirdDict['Nickname'] != '':
        nick = tBirdDict['Nickname']

    if nick == None or nick == '':
            #pdb.set_trace()
            pass 

    return nick, vObjDict 

for c in contacts:
    nick, dict = dict_from_thunderbird_dict(c)
    if nick == None:
        pdb.set_trace()
    else:
        vcard = vobject.vCard()
        config = pypeople.get_config()
        pdb.set_trace()
        pypeople.vcard_from_dict(dict,vcard)
        pdb.set_trace()


#Fuuuu. Convert to some vobject



