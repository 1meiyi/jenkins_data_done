import json
import os
from datetime import datetime
import jenkins
import requests
from dotenv import load_dotenv
from atlassian import Confluence
import pandas as pd
import re
from ast import literal_eval

load_dotenv('./yi.mei.env')

jenkins_url = os.getenv("JENKINS_URL")
username = os.getenv("JENKINS_USERNAME")
api_token = os.getenv("JENKINS_API_TOKEN")
server = jenkins.Jenkins(
    url=jenkins_url,
    username=username,
    password=api_token)

new_build_job = None
new_allure = None
new_build = None
# main_builds_info = server.get_job_info('compute_release_ci_test_ddk2.0')
# builds = main_builds_info['builds'][:7]  # master s80 s3000 s4000 s5000  kuae：s3000 s4000
# recent_builds = []
# err_result = ''
# for build in builds:
#     build_number = build['number']
# build_info = server.get_build_info('compute_release_ci_test_ddk2.0', 1023)
build_info = server.get_build_info('daily.musa_sdk', 196)
# http://sh-jenkins.mthreads.com/job/daily.musa_sdk/
# print(build_info)


# print(confluence_table)

report_date = datetime.now().strftime("%Y_%m_%d")
def parse_log():
    with open('./ddk.log', 'r', encoding='utf-8') as f:
        log_str = f.read()
    tests = []
    current_test = {}
    test_name_pattern = re.compile(r'(INFO|ERROR):root:([\w-]+)')
    failed_pattern = re.compile(r'failed: (\d+)')
    passed_pattern = re.compile(r'passed case: (\d+)')
    failed_cases_pattern = re.compile(r'失败测试用例:(.*?\'])')

    for block in log_str.split('------------------------------------------'):
        if match := test_name_pattern.search(block):
            status, test_name = match.groups()
            if test_name != current_test.get('task Name'):
                if current_test:
                    # 计算通过率
                    total = current_test['passed cases'] + current_test['failed cases']
                    rating = (current_test['passed cases'] / total * 100) if total != 0 else 0.0
                    current_test['task rating'] = f"{rating:.2f}%"
                    tests.append(current_test)
                current_test = {
                    'task Name': test_name,
                    'passed cases': 0,
                    'failed cases': 0,
                    'task rating': '',
                    'failed test cases': ''
                }
        if match := failed_pattern.search(block):
            current_test['failed cases'] = int(match.group(1))
        if match := passed_pattern.search(block):
            current_test['passed cases'] = int(match.group(1))
        if match := failed_cases_pattern.findall(block):
            try:
                cases = literal_eval(match[0])
                current_test['failed test cases'] = cases
            except:
                current_test['failed test cases'] = 'N/A'
    if current_test:
        total = current_test['passed cases'] + current_test['failed cases']
        rating = (current_test['passed cases'] / total * 100) if total != 0 else 0.0
        current_test['task rating'] = f"{rating:.2f}%"
        tests.append(current_test)

    return pd.DataFrame(tests)
# 生成 DataFrame
df = parse_log()

# 导出到Excel
df.to_excel(f"{report_date}_test_results.xlsx", index=False)
print(df)


