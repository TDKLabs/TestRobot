
import tdk
import os
import sst.actions
import datetime
from robot.api import logger


logger.debug(" ... Importing tdk_utils library ... ")

class tdk_utils:

    def __init__(self):
        logger.debug(" ... in tdk_utils constructor ... ")


    def capture_screenshot(self):
        logger.debug(" ... in tdk_utils.capture_screenshot ... ")

        filename = '%s.png' % ('selenium-'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        sst.actions.take_screenshot(filename)
  

    def get_jboss_time(self, server_ip, username='devlocal', password='Sh0wThe$$'):
        logger.debug(" ... in tdk_utils.get_jboss_time ... ")
        import paramiko
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        logger.debug(" running remote command: ('date') on host: (%s) " % server_ip)
        stdin, stdout, stderr = ssh.exec_command('date')
        mesg = stdout.read()
        logger.debug(" date returned: (%s) " % mesg)
                
        ssh.close()
        return mesg
    
    
    def get_jboss_log(self, server_ip, log='/log/server.log', username='devlocal', password='Sh0wThe$$', lines='50000'):
        logger.debug(" ... in tdk_utils.get_jboss_log ... ")
        import paramiko
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        logger.debug(" running remote command: ('tail') on host: (%s) " % server_ip)
        stdin, stdout, stderr = ssh.exec_command('tail -n %s %s' % (lines, log))
        mesg = stdout.read()
        logger.debug(" tail returned: (%s) " % mesg)
                
        ssh.close()
        return mesg
    