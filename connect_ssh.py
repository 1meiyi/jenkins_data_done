import logging
import paramiko



class Test:
    ssh = None

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ssh = paramiko.SSHClient()
        # self.log = logging
        self.log = logging.getLogger(__name__)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def login(self, host):
        try:
            self.ssh.connect(host, port=22, username='root', password='QAQqaq@98.178')
            self.log.info('Connected to %s successfully.', host)
        except Exception as e:
            self.log.error('Failed to connect to %s: %s', host, e)
            raise

    def send(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if stdin:
            self.log.info(f'exec cmd: %s', cmd)
        if stdout:
            self.log.info('sucess: \n %s', stdout.strip())
        else:
            self.log.warning('None output')
        if stderr:
            self.log.error('error: %s', stderr.strip())
        return stdout

    def close(self):
        self.ssh.close()

