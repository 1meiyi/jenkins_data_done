import argparse
import logging
import connect_ssh
import re
import robot


class Check_node():
    def __init__(self):
        self.ssh = connect_ssh.Test()
        self.token = "b36df80a7464823ca6c928f649f0e056d58462adce9057d55f07ff17d0b9acc5"
        self.secret = "SEC44b85d6cfe5812423e4482d5b50c7c193631cd1aa0e29833c77e28e9ed97705d"
        self.o = robot.Robot(self.token, self.secret)
        logging.basicConfig(level=logging.INFO, format='\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)

    def args_env(self):
        parser = argparse.ArgumentParser(description="选择分支")
        parser.add_argument("-f", "--farm", help="-f dailyfarm 选择dailyfarm集群 -f releasefarm 选择releasefarm集群 ",
                            default="none")
        args = parser.parse_args()
        return args

    def node_check(self):
        res = True
        farm = self.args_env().farm
        rs = self.ssh.send(
            f'kubectl get node $1 -L GPU_TYPE -L GPU_TEST_TYPE -L HOST_TYPE -L PLATFORM -L mt --context {farm}')
        lines = rs.strip().split('\n')
        res_list = []
        del lines[0]
        for i in lines:
            if i != lines[-1]:
                headers = re.split(r'\s+', i)  # 提取列名
                rs_dict = {
                    'IP': f'{headers[0]}',
                    'STATUS': f'{headers[1]}',
                    'ROLES': f'{headers[2]}',
                    'VERSION': f'{headers[3]}',
                    'AGE': f'{headers[4]}',
                    'GPU_TYPE': f'{headers[5]}',
                    'GPU_TEST_TYPE': f'{headers[6]}',
                    'HOST_TYPE': f'{headers[7]}',
                    'PLATFORM': f'{headers[8]}',
                }
                res_list.append(rs_dict)
            else:
                headers = re.split(r'\s+', i)
                rs_dict = {
                    'IP': f'{headers[0]}',
                    'STATUS': f'{headers[1]}',
                    'ROLES': f'{headers[2]}',
                    'VERSION': f'{headers[3]}',
                    'AGE': f'{headers[4]}',
                }
                res_list.append(rs_dict)
        exec_IP = []
        for i in res_list:
            if i.get('STATUS') != 'Ready':
                exec_IP.append(i.get('IP'))
        if exec_IP:
            res = False
            self.log.error("NODE STATUS IS NOT Ready!")
        else:
            self.log.info("NODE STATUS IS Ready!")
        return res, exec_IP

    def check_status(self):
        res = True
        farm = self.args_env().farm
        rs = self.ssh.send(f'kubectl get nodeconfig --context  {farm}')
        lines = rs.strip().split('\n')
        del lines[0]
        res_list = []
        for i in lines:
            headers = re.split(r'\s+', i)  # 提取列名
            rs_dict = {
                'IP': f'{headers[0]}',
                'DRIVER UPGRADE STATE': f'{headers[1]}',
                'NODE POOL ': f'{headers[2]}',
            }
            res_list.append(rs_dict)
        exec_IP = []
        for i in res_list:
            if i.get('DRIVER UPGRADE STATE') != 'InstallDone':
                exec_IP.append(i.get('IP'))
        if exec_IP:
            res = False
            self.log.error("DRIVER STATE IS NOT InstallDone!")
        else:
            self.log.info("DRIVER STATE IS InstallDone!")
        return res, exec_IP

    def main(self):
        self.ssh.login(host='192.168.98.178')
        farm = self.args_env().farm
        res = True
        res_nodeconfig, exec_ip_nodeconfig = self.check_status()
        res_nodestatus, exec_ip_nodestatus = self.node_check()
        res = res_nodeconfig and res_nodestatus
        # if not res:
        #     self.o.send_text(f"{farm}:\nnode 或 nodeconfig状态异常，请检查！\n异常节点: \n{exec_ip_nodestatus} ",
        #                      ['1bb-qgn5shbiod'])
        # else:
        #     self.log.info("Good!")
        #     self.o.send_text(f'{farm}: \nnode和nodeconfig状态无异常', ['1bb-qgn5shbiod'])
        # self.ssh.close()


if __name__ == '__main__':
    C = Check_node()
    C.main()
