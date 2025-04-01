#! /usr/bin/env python3
import datetime
import os
import argparse
import requests
import json
import base64
from requests.utils import dict_from_cookiejar
import subprocess
import logging

data_env = {
    'gpu_info': ['s80', 's3000', 's4000', 's5000'],
    'cts_case': ['OPENCL_MUSA_API',
                 'MUSA_THIRD_PARTY_AND_HIP_TEST',
                 'MUSA_FUNCTIONAL',
                 'ptsz',
                 'MUSA_STRESS_TEST',
                 'cuda_sample'],
    'ddk_case': ['800_test_musa_cts/musa_mtcc',
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
}

logging.basicConfig(level=logging.INFO)


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

        self.log = logging.getLogger()

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
                # 请求网址返回session id
                res = self.requests.post(url=self.url + path, data=self.payload, headers=headers, timeout=15)
                if f'{res.status_code}'.startswith('2'):
                    try:
                        # 获取并返回token
                        self.token = dict_from_cookiejar(res.cookies)['token']
                        return self.token
                    except AttributeError:
                        print('服务器超时')
                else:
                    continue
            except requests.exceptions.ReadTimeout:
                print('连接超时，无法获取token')

    def get_buckets(self):
        print('仓库')
        response = self.requests.get(f'{self.url}{self.buckets}')
        print(response.status_code)

    def args_env(self):
        parser = argparse.ArgumentParser(description="mtcc_cts、ddk")
        parser.add_argument("-b", "--branch", help="-b master 选择master分支 -b kuae 选择release分支", default="none")
        parser.add_argument("-p", "--product", help="-p ddk 选择driver—ddk -p cts 选择mtcc_cts", default="none")
        args = parser.parse_args()
        return args

    def get_allure_package(self, days_offset=1, time_date=None):
        url_list = []
        branch = self.args_env().branch
        product = self.args_env().product
        case_list = product + '_case'
        if not time_date:
            t = datetime.datetime.now() - datetime.timedelta(days=days_offset)
            time_date = t.strftime("%Y-%m-%d")
        for info in data_env['gpu_info']:
            driver_pa = f'driver_toolkits_test/{info}'
            for case in data_env[f'{case_list}']:
                if product == 'cts':
                    dict_addr = {
                        'addr': f'/800_test_musa_cts/{case}'}
                elif product == 'ddk':
                    dict_addr = {
                        'addr': f'/{case}'}
                ddr_url = driver_pa + dict_addr['addr']
                finally_url = self.enbase(f'computeQA/cuda_compatible/CI/{branch}/{time_date}/{ddr_url}/')
                url_list.append(finally_url)
        return url_list

    def download_allure(self):
        for i in self.get_allure_package():
            test_case = self.debase(i).split('/')
            if test_case[-3] == '800_test_musa_cts':
                test_info = f'{test_case[-4]}-{test_case[-2]}'
            else:
                test_info = f'{test_case[-3]}-{test_case[-2]}'
            try:
                allure_name = [file['name'] for file in
                               self.requests.get(f'{self.url}{self.buckets}release-ci/objects?prefix={i}',
                                                 headers=self.get_headers()).json()['objects'] if
                               file['name'].endswith('_result.tar.gz') or file['name'].endswith('_result_.tar.gz') or
                               file['name'].endswith('allure_report.tar.gz') and 'assembler' not in file['name']]
                if allure_name:
                    for d_source in allure_name:
                        # self.log.info(f'正在下载：https://oss.mthreads.com/release-ci/{d_source}')
                        self.run_command(f'rm -rf ./testreport/*')
                        self.run_command(
                            f'wget https://oss.mthreads.com/release-ci/{d_source} -O ./testreport/{test_case[-2]}.tar.tgz')
                        self.run_command(
                            f' mkdir -p ./testreport/{test_case[-2]} && tar -xvf ./testreport/{test_case[-2]}.tar.tgz  -C ./testreport/{test_case[-2]}')
                        self.get_allure_info(f'./testreport/{test_case[-2]}/', test_info)
                else:
                    self.log.error(f'{test_info}-未上传报告')
            except (KeyError, TypeError):
                self.log.error(f'{test_info}-测试异常')

    def run_command(self, cmd):
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            self.log.error(f"Error cmd: {e}")

    def get_all_files_scandir(self, dire):
        all_files = []
        try:
            for entry in os.scandir(dire):
                if entry.is_file():
                    all_files.append(entry.path)
                elif entry.is_dir():
                    all_files.extend(self.get_all_files_scandir(entry.path))
        except PermissionError:
            print(f"无访问权限目录 {dire}")
        return all_files

    def get_allure_info(self, path, info):
        count_pass = 0
        count_fail = 0
        count_broken = 0
        count_sample_fail = 0
        count_sample_pass = 0
        failcase = []
        files = self.get_all_files_scandir(path)
        for filename in files:
            if filename.endswith("-result.json"):
                with open(filename, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    test_case = {
                        "name": data.get("name"),
                        "status": data.get("status"),
                        "case_name": data.get('parameters')[0]['value']
                    }

                if test_case is None:
                    self.log.error('获取到空字段')
                elif test_case['status'] == 'failed':
                    count_fail += 1

                    failed_case = test_case['name']
                    failcase.append(failed_case)
                elif test_case['status'] == 'passed':
                    count_pass += 1
                elif test_case['status'] == 'broken':
                    count_broken += 1
        if count_fail > 0:
            self.log.error(f'{info} failed: {count_fail}条')
            self.log.info(f'{info} 失败测试用例:{failcase}')
            self.log.info(f'{info} passed case: {count_pass} 条')
        elif count_broken > 0:
            self.log.warning(f'{info} broken case: {count_broken} 条')
        elif count_pass > 0:
            self.log.info(f'{info} passed case: {count_pass} 条')

    def enbase(self, path):
        prefix = base64.urlsafe_b64encode(path.encode()).decode()
        return prefix

    def debase(self, path):
        prefix = base64.urlsafe_b64decode(path.encode()).decode()
        return prefix


if __name__ == '__main__':
    fp = Autoinstall()
    fp.get_session()
    fp.download_allure()

# check_allure_report.py > op_jenkins.get_build_rs() 处理返回字典套列表的结果

