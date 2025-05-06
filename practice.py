import json
import os
import re
from datetime import datetime
import jenkins
import requests

# from dotenv import load_dotenv
# from atlassian import Confluence
#
# load_dotenv('./yi.mei.env')
# confluence_url = os.getenv("CONFLUENCE_URL")
# confluence_name = os.getenv("CONFLUENCE_USERNAME")
# confluence_token = os.getenv("CONFLUENCE_TOKEN")
# print(confluence_url, confluence_name, confluence_token)
# confluence = Confluence(
#     url=confluence_url,
#     username=confluence_name,
#     password=confluence_token,
#     cloud=False)
#
# parent_id = confluence.get_page_id(space="SWQA", title='Compute_release_ci_test_ddk2.0 结果记录')
# print(parent_id)

data_env = {
    'gpu_info': ['s80', 's3000', 's4000', 's5000'],
    'cts_case': ['OPENCL_MUSA_API',
                 'MUSA_THIRD_PARTY_AND_HIP_TEST',
                 'MUSA_FUNCTIONAL',
                 'ptsz',
                 'MUSA_STRESS_TEST',
                 'cuda_sample',
                 'test.mudnn_cts'],
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
import pandas as pd
import os


def get_smoke_case():
    smoke_case = []
    file_name = os.listdir('./csv')
    for i in file_name:
        if i.endswith('csv'):
            rs = pd.read_csv('./csv/' + i)
            dict_list = rs.to_dict(orient='records')
            for j in dict_list:
                try:
                    if 'smoke' in j.get('type') or 'smoke' in j.get('test_type') or 'smoke' in j.get('quyuan_type'):
                        # rs1 = f'{i} {j.get('case')}\n'
                        smoke_case.append(j.get('case'))
                except TypeError:
                    pass
    return smoke_case

# musa_cts smokeM3D
def get_fail_case():
    global file_name
    fail_cases = []
    rs = pd.read_excel('./2025_04_27_test_results.xlsx')
    dict_list = rs.to_dict(orient='records')
    for i in dict_list:
        fail_case = str(i.get('failed test cases'))
        try:
            rs = re.findall(r'\[(.*?)\]', fail_case)
            for j in rs:
                for x in j.strip('\"').split('['):
                    fail_cases.append(x)
        except AttributeError:
            pass
    smoke_case = get_smoke_case()
    failed_in_smoke = [fail for fail in smoke_case if fail in fail_cases]
    for q in failed_in_smoke:
        for w in dict_list:
            if q in str(w.get('failed test cases')):
                print(w.get('task Name'), q)
get_fail_case()
