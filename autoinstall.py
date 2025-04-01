import datetime
import os
import re
import requests
import json
import base64
from requests.utils import dict_from_cookiejar
import subprocess
import logging

gpu_info = ['s80', 's3000', 's4000', 's5000']
cts_case = ['OPENCL_MUSA_API',
            'MUSA_THIRD_PARTY_AND_HIP_TEST',
            'MUSA_FUNCTIONAL',
            'ptsz',
            'MUSA_STRESS_TEST']

ddk_case = ['800_test_musa_cts/musa_mtcc',
            '801_test_mtcc_test',
            '822_test_muBLAS_cts',
            '825_test_muRAND_cts',
            '823_test_muFFT_cts',
            '828_test_muSPARSE_cts_daily',
            '828_test_muSPARSE_cts_weekly_part1',
            '828_test_muSPARSE_cts_weekly_part2',
            '824_test_muPP_cts',
            '829_test_muSOLVER_cts',
            '827_test_muAlg_cts',
            '826_test_muThrust_cts']

logging.basicConfig(level=logging.INFO, format='\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Autoinstall:
    def __init__(self):
        # 定义payload
        self.payload = json.dumps({
            "accessKey": "mtoss",
            "secretKey": "mtoss123"
        })
        try:
            # 初始化句柄
            self.requests = requests.session()
        except requests.exceptions.ReadTimeout:
            print('连接服务器超时')
        self.url = 'https://oss.mthreads.com:9001/api/v1/'
        self.buckets = 'buckets/'

        self.log = logging.getLogger(__name__)

    def get_headers(self):
        # 定义全局headers
        return {
            'Content-Type': 'application/json',
            'Cookie': f"token={self.token}",
        }

    def get_session(self):
        path = 'login'
        # 定义header
        headers = {
            'Content-Type': 'application/json'}
        for i in range(5):
            try:
                print(f'第{i + 1}次尝试获取session id')
                # 请求网址返回session id
                res = self.requests.post(url=self.url + path, data=self.payload, headers=headers, timeout=15)
                print(res.status_code)
                if f'{res.status_code}'.startswith('2'):
                    try:
                        # 获取并返回token
                        self.token = dict_from_cookiejar(res.cookies)['token']
                        print('成功获取session id')
                        return self.token
                    except AttributeError:
                        print('服务器超时')
                else:
                    print(f'第{i + 1}次尝试连接')
                    continue
            except requests.exceptions.ReadTimeout:
                print('连接超时，无法获取token')

    def get_buckets(self):
        print('仓库')
        response = self.requests.get(f'{self.url}{self.buckets}')
        print(response.status_code)

    def get_master_musa_cts(self):
        if datetime.datetime(2025, int(datetime.datetime.now().strftime('%m')),
                             int(datetime.datetime.now().strftime('%d')),
                             15, 30, 00) - datetime.datetime.today() > datetime.timedelta(hours=0, minutes=0):
            file_time = -1
        else:
            file_time = -2
        # 编码仓库地址
        prefix = self.enbase('computeQA/cuda_compatible/CI/master/')
        # 拼接 url
        url = f'{self.url}{self.buckets}release-ci/objects?prefix={prefix}'
        # 根据时间获取最新Allure报告
        time_date = self.requests.get(url, headers=self.get_headers()).json()['objects'][file_time]['name']
        # for i in range(16):
        for info in gpu_info:
            for case in cts_case:
                opencl_musa_api = {  # OPENCL_MUSA_API
                    'opencl_musa_api': f'driver_toolkits_test/{info}/800_test_musa_cts/{case}/',
                }
                allure_url = f'{self.url}{self.buckets}release-ci/objects?prefix={self.enbase(f'{time_date}{opencl_musa_api['opencl_musa_api']}')}'
                try:
                    allure_name = [i['name'] for i in
                                   self.requests.get(allure_url.strip(), headers=self.get_headers()).json()['objects']
                                   if
                                   i['name'].endswith('allure_result.tar.gz')]
                    for d_source in allure_name:
                        if 'assembler' not in d_source:
                            self.run_command(f'wget https://oss.mthreads.com/release-ci/{d_source}')
                            print(f'正在下载：https://oss.mthreads.com/release-ci/{d_source}')
                            self.run_command(
                                f' mkdir ./testreport/{case} && tar -xvf {d_source.split('/')[-1]} -C ./testreport/{case}')
                            self.get_allure_info(f'./testreport/{case}')
                except (KeyError, TypeError):
                    print(f'{info}-{case}测试异常，请前往blue ocean检查')

    def get_master_ddk(self,days_offset=1, time_date='2025-03-21'):
        if not time_date:
            t = datetime.datetime.now() - datetime.timedelta(days=days_offset)
            time_date = t.strftime("%Y-%m-%d")
        # # 编码仓库地址
        prefix = self.enbase('computeQA/cuda_compatible/CI/master/')
        # 拼接 url
        # url = f'{self.url}{self.buckets}release-ci/objects?prefix={prefix}'
        # 根据时间获取最新Allure报告
        # time_date = self.requests.get(url, headers=self.get_headers()).json()['objects'][time_date]['name']
        for info in gpu_info:
            for case in ddk_case:
                allure_address = {  # OPENCL_MUSA_API
                    'address': f'driver_toolkits_test/{info}/{case}',
                }
                print(allure_address)
                allure_url = f'{self.url}{self.buckets}release-ci/objects?prefix={prefix}{self.enbase(f'{time_date}/{allure_address['address']}/')}'
                print(allure_url)
                try:
                    allure_name = [i['name'] for i in
                                   self.requests.get(allure_url.strip(), headers=self.get_headers()).json()['objects']
                                   if i['name'].endswith('allure_report.tar.gz')]
                    print(allure_name)
                    for d_source in allure_name:
                        if 'assembler' not in d_source:
                            # self.run_command(f'wget https://oss.mthreads.com/release-ci/{d_source}')
                            print(f'正在下载：https://oss.mthreads.com/release-ci/{d_source}')
                            # self.run_command(
                            #     f' mkdir ./testreport/{case} && tar -xvf {d_source.split('/')[-1]} -C ./testreport/{case}')
                            # self.get_allure_info(f'./testreport/{case}')
                except (KeyError, TypeError):
                    print(f'{info}-{case}测试异常，请前往blue ocean检查')

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, check=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            if result.stdin:
                self.log.info(f'exec cmd：%s\n', cmd)
            if result.stdout:
                self.log.info('sucess ：%s\n', result.stdout.strip())
            else:
                self.log.warning('None output\n')
            if result.stderr:
                self.log.error('error：%s\n', result.stderr.strip())
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error cmd: {e}")

    def get_allure_info(self, path):
        count_pass = 0
        count_fail = 0
        count_broken = 0
        for filename in os.listdir(path):
            if filename.endswith("-result.json"):
                file_path = os.path.join(path, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    test_case = {
                        "name": data.get("name"),
                        "status": data.get("status"),
                        "case_name": data.get('parameters')[0]['value']
                    }
                    if test_case is None:
                        print('获取到空字段')
                    elif test_case['status'] == 'failed':
                        count_fail += 1
                        print(f'失败测试用例：{test_case['case_name']}')
                    elif test_case['status'] == 'passed':
                        count_pass += 1
                    elif test_case['status'] == 'broken':
                        count_broken += 1
        if count_fail > 0:
            print(f' failed case: {count_fail} 条')
        elif count_broken > 0:
            print(f' broken case: {count_broken} 条')

        print(f' passed case: {count_pass} 条')

    def enbase(self, path):
        prefix = base64.urlsafe_b64encode(path.encode()).decode()
        return prefix

    def debase(self, path):
        prefix = base64.urlsafe_b64decode(path.encode()).decode()
        return prefix


if __name__ == '__main__':
    fp = Autoinstall()
    fp.get_session()
    fp.get_master_musa_cts()
    fp.get_master_ddk()
