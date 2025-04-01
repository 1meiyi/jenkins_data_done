import json
import os
import re
from datetime import datetime
import jenkins
import requests
from dotenv import load_dotenv
from atlassian import Confluence

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
build_info = server.get_build_info('compute_release_ci_test_ddk2.0', 905)



# build_url = re.findall('http://sh-jenkins.mthreads.com/job.*?[0-9+]/',
#                        build_info.get('description'))  # 构建与报告url
# gpu_type = re.findall('gpu_type: (.*?)</b>', build_info.get('description'))  # gpu_type
# print(gpu_type)

# print(f'http://sh-jenkins.mthreads.com/job/compute_release_ci_test_ddk2.0/{build_number}')
