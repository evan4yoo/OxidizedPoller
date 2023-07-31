import ipaddress

#Rename this to config.py
#Fill in the below
#Adjust directory in main.py
directory = r"C:\Users\E\PycharmProjects\OxidizedPoller"

secrets = {
#User is for SSH login to read system
    'user': "InstallSSHUserHere",
#Pass is for SSH password to read system
    'pass': "InstallSSHPasswordHere",
#OxiUser is for Oxidized config build
    'oxiuser': "InstallOxiUserHere",
#OxiSecret is for Oxidized config build
    'oxisecret': "installOxiSecretHere"
}

networks = [
    ipaddress.ip_network('192.168.0.0/24'),
    ipaddress.ip_network('192.169.1.0/24')
]

##Stop messing with things