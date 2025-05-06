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
import csv
import pandas as pd
data_env = {
    'cts_case': ['s80/800_test_musa_cts/MUSA_THIRD_PARTY_AND_HIP_TEST',
                 's80/800_test_musa_cts/OPENCL_MUSA_API',
                 's80/800_test_musa_cts/MUSA_STRESS_TEST'
                 's80/800_test_musa_cts/MUSA_FUNCTIONAL',
                 's80/800_test_musa_cts/ptsz',
                 's3000/800_test_musa_cts/OPENCL_MUSA_API',
                 's3000/800_test_musa_cts/MUSA_THIRD_PARTY_AND_HIP_TEST',
                 's3000/800_test_musa_cts/MUSA_FUNCTIONAL',
                 's3000/800_test_musa_cts/ptsz',
                 's3000/800_test_musa_cts/MUSA_STRESS_TEST',
                 's4000/800_test_musa_cts/OPENCL_MUSA_API',
                 's4000/800_test_musa_cts/MUSA_THIRD_PARTY_AND_HIP_TEST',
                 's4000/800_test_musa_cts/MUSA_FUNCTIONAL',
                 's4000/800_test_musa_cts/ptsz',
                 's4000/800_test_musa_cts/MUSA_STRESS_TEST',
                 's4000/800_test_musa_cts/MULTI_DEV',
                 's4000/test.mudnn_cts',
                 's5000/800_test_musa_cts/OPENCL_MUSA_API',
                 's5000/800_test_musa_cts/MUSA_THIRD_PARTY_AND_HIP_TEST',
                 's5000/800_test_musa_cts/MUSA_FUNCTIONAL',
                 's5000/800_test_musa_cts/ptsz',
                 's5000/800_test_musa_cts/MUSA_STRESS_TEST',
                 's5000/800_test_musa_cts/MULTI_DEV',
                 's5000/test.mudnn_cts'
                 ],
    'ddk_case': ['s80/800_test_musa_cts/musa_mtcc',
                 's80/801_test_mtcc_test',
                 's80/822_test_muBLAS_cts',
                 's80/825_test_muRAND_cts',
                 's80/823_test_muFFT_cts',
                 's80/828_test_muSPARSE_cts_daily',
                 's80/828_test_muSPARSE_cts_weekly_part1',
                 's80/828_test_muSPARSE_cts_weekly_part2',
                 's80/824_test_muPP_cts',
                 's80/829_test_muSOLVER_cts',
                 's80/827_test_muAlg_cts',
                 's80/826_test_muThrust_cts',
                 's3000/800_test_musa_cts/musa_mtcc',
                 's3000/801_test_mtcc_test',
                 's3000/822_test_muBLAS_cts',
                 's3000/825_test_muRAND_cts',
                 's3000/823_test_muFFT_cts',
                 's3000/828_test_muSPARSE_cts_daily',
                 's3000/828_test_muSPARSE_cts_weekly_part1',
                 's3000/828_test_muSPARSE_cts_weekly_part2',
                 's3000/824_test_muPP_cts',
                 's3000/829_test_muSOLVER_cts',
                 's3000/827_test_muAlg_cts',
                 's3000/826_test_muThrust_cts',
                 's4000/800_test_musa_cts/musa_mtcc',
                 's4000/801_test_mtcc_test',
                 's4000/822_test_muBLAS_cts',
                 's4000/825_test_muRAND_cts',
                 's4000/823_test_muFFT_cts',
                 's4000/828_test_muSPARSE_cts_daily',
                 's4000/828_test_muSPARSE_cts_weekly_part1',
                 's4000/828_test_muSPARSE_cts_weekly_part2',
                 's4000/824_test_muPP_cts',
                 's4000/829_test_muSOLVER_cts',
                 's4000/827_test_muAlg_cts',
                 's4000/826_test_muThrust_cts',
                 's5000/800_test_musa_cts/musa_mtcc',
                 's5000/801_test_mtcc_test',
                 's5000/822_test_muBLAS_cts',
                 's5000/825_test_muRAND_cts',
                 's5000/823_test_muFFT_cts',
                 's5000/828_test_muSPARSE_cts_daily',
                 's5000/828_test_muSPARSE_cts_weekly_part1',
                 's5000/828_test_muSPARSE_cts_weekly_part2',
                 's5000/824_test_muPP_cts',
                 's5000/829_test_muSOLVER_cts',
                 's5000/827_test_muAlg_cts',
                 's5000/826_test_muThrust_cts'],
    'kuae_M3D': ['s5000/800_test_musa_cts/musa_mtcc',
                 's5000/801_test_mtcc_test',
                 's5000/822_test_muBLAS_cts',
                 's5000/825_test_muRAND_cts',
                 's5000/823_test_muFFT_cts',
                 's4000/800_test_musa_cts/musa_mtcc',
                 's4000/801_test_mtcc_test',
                 's4000/822_test_muBLAS_cts',
                 's4000/825_test_muRAND_cts',
                 's4000/823_test_muFFT_cts',
                 's3000/800_test_musa_cts/musa_mtcc',
                 's3000/801_test_mtcc_test',
                 's3000/822_test_muBLAS_cts',
                 's3000/825_test_muRAND_cts',
                 's3000/823_test_muFFT_cts',
                 's80/800_test_musa_cts/musa_mtcc',
                 's80/801_test_mtcc_test',
                 's80/822_test_muBLAS_cts',
                 's80/825_test_muRAND_cts',
                 's80/823_test_muFFT_cts',
                 ]

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
        global branch
        url_list = []
        branch = self.args_env().branch
        product = self.args_env().product
        if branch == 'kuae':
            branch = 'release_KUAE_2.0_for_PH1_M3D'
            case_list = 'kuae_M3D'
        else:
            case_list = product + '_case'
        if not time_date:
            t = datetime.datetime.now() - datetime.timedelta(days=days_offset)
            time_date = t.strftime("%Y-%m-%d")
        for case in data_env[f'{case_list}']:
            finally_url = self.enbase(f'computeQA/cuda_compatible/CI/{branch}/{time_date}/driver_toolkits_test/{case}/')
            url_list.append(finally_url)
        #       print(url_list)
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
                        #                        self.log.info(f'正在下载：https://oss.mthreads.com/release-ci/{d_source}')
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
        sam_fail = 0
        sam_pass = 0
        ptsz_fail = 0
        ptsz_pass = 0
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
                if info.strip().split('-')[-1] == 'ptsz':
                    if 'test_musa_ptsz' in test_case['name']:
                        if test_case['status'] == 'failed':
                            ptsz_fail += 1
                        elif test_case['status'] == 'passed':
                            ptsz_pass += 1
                if 'test_musa_cuda_samples' in test_case['name']:
                    if test_case['status'] == 'failed':
                        sam_fail += 1
                    elif test_case['status'] == 'passed':
                        sam_pass += 1
                elif test_case['status'] == 'failed':
                    count_fail += 1
                    failed_case = test_case['name']
                    failcase.append(failed_case)
                elif test_case['status'] == 'passed':
                    count_pass += 1
                elif test_case['status'] == 'broken':
                    count_broken += 1
        if info.strip().split('-')[-1] != 'ptsz':
            if count_fail > 0:
                self.log.error(f'{info} failed: {count_fail}条')
                self.log.info(f'{info} 失败测试用例:{failcase}')
                self.log.info(f'{info} passed case: {count_pass} 条')

                # df = pd.DataFrame()
                # row_df = pd.DataFrame([{'ddk_task': info,
                #                         'passed': count_pass,
                #                         'failed': count_fail,
                #                         'passRating': "{:.2%}".format(count_pass / (count_pass + count_fail)),
                #                         'failed_cases': failcase
                #                         }])
                #
                # # 合并到主 DataFrame
                # df = pd.concat([df, row_df], ignore_index=True)
                # print(df.tail())

            elif count_broken > 0:
                self.log.warning(f'{info} broken case: {count_broken} 条')
            elif count_pass > 0:
                self.log.info(f'{info} passed case: {count_pass} 条')
        if sam_pass > 0:
            gpu_info = info.split('-')[0]
            self.log.info(f'{gpu_info}cuda_samples faild: {sam_fail}条')
            self.log.info(f'{gpu_info} cuda_samples pass: {sam_pass}条')

        if ptsz_pass > 0:
            self.log.info(f'{info} faild: {ptsz_fail}条')
            self.log.info(f'{info} pass: {ptsz_pass}条')
        print('------------------------------------------')

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
