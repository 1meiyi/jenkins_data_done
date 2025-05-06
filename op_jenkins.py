import json
import os
import re
from datetime import datetime
import jenkins
import pandas as pd
from dotenv import load_dotenv
from ast import literal_eval
from atlassian import Confluence

jobs = ['800_test_musa_cts_gitlab',
        '801_test_mtcc_test_gitlab',
        '822_test_muBLAS_cts_gitlab',
        '823_test_muFFT_cts_gitlab',
        '824_test_muPP_cts_gitlab',
        '825_test_muRAND_cts_gitlab',
        '826_test_muThrust_cts_gitlab',
        '827_test_muAlg_cts_gitlab',
        '828_test_muSPARSE_cts_gitlab',
        '829_test_muSOLVER_cts_gitlab', ]

load_dotenv('./yi.mei.env')


# 加载当前目录下env文件

class Send_ding_report:

    def __init__(self):
        # 初始化登录jenkins与confluence数据
        jenkins_url = os.getenv("JENKINS_URL")
        username = os.getenv("JENKINS_USERNAME")
        api_token = os.getenv("JENKINS_API_TOKEN")
        self.server = jenkins.Jenkins(
            url=jenkins_url,
            username=username,
            password=api_token)
        confluence_url = os.getenv("CONFLUENCE_URL")
        confluence_name = os.getenv("CONFLUENCE_USERNAME")
        confluence_token = os.getenv("CONFLUENCE_TOKEN")
        self.confluence = Confluence(
            url=confluence_url,  # Confluence 站点 URL
            username=confluence_name,  # 登录邮箱
            password=confluence_token,  # API Token #MjgyNzcyMTU4MDYyOvxtaVqaP+1Dx/yi3kJf8esLiu/9
            cloud=False  # 是否是云版confluence
        )

    def make_build_daily(self):
        # 获取Jenkins 任务列表并将信息组成json
        new_build = None
        main_builds_info = self.server.get_job_info('compute_release_ci_test_ddk2.0')
        builds = main_builds_info['builds'][:7]  # master s80 s3000 s4000 s5000  kuae：s3000 s4000 s5000
        # Daily任务 7个
        recent_builds = []
        err_result = ''
        for build in builds:
            build_number = build['number']
            build_info = self.server.get_build_info('compute_release_ci_test_ddk2.0', build_number)
            commit_id = re.findall(r'ddk_commit_id: (\w{9})', build_info.get('description'))  # commit_id
            branch_farm = re.search('Farm: (.*?)</b>', build_info.get('description')).group(1)  # branch
            build_time = str(datetime.fromtimestamp(build_info.get('timestamp') / 1000).strftime('%Y/%m/%d'))
            build_url = f'http://sh-jenkins.mthreads.com/job/compute_release_ci_test_ddk2.0/{build_number}'
            gpu_type = re.findall('gpu_type: (.*?)</b>', build_info.get('description'))  # gpu_type
            # 匹配数据
            try:
                recent_builds.append({
                    'branch_farm': branch_farm,
                    'gpu_type': gpu_type[0],
                    'build_commit_id': commit_id[0],
                    'build_time': build_time,
                    "build_url": build_url,
                    "status": build_info.get('result'),
                    "is_building": str(build_info.get('inProgress')),
                })
            except TypeError:
                print(f'Farm: {branch_farm} GPU: {gpu_type} Commit id: {commit_id[0]}, 构建异常 请检查')
        self.write_data_to_json(recent_builds)
        # 写入本地json文件
        return recent_builds

    def write_data_to_json(self, json_data):
        # 写入json
        with open("data.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data, ensure_ascii=False, sort_keys=True, indent=4))

    def update_confluence(self, product):
        """
        构建Jenkins数据、并上传confluence。
        :param product:
        :return:
        """
        page_true = None
        report_date = datetime.now().strftime("%Y-%m-%d")
        try:
            page_true = self.confluence.get_page_by_title(space="SWQA", title=f"{report_date}")
        except AttributeError:
            print('页面未创建')

        if not page_true:
            self.confluence.create_page(
                parent_id=242474903,
                space='SWQA',
                title=f'{report_date}',
                body='')
        confluence_table = ''
        df = pd.read_excel('test_results.xlsx')
        dict_list = df.to_dict(orient='records')
        for i in dict_list:
            table = f"""
                      <tr>  
                        <td>{i.get('task Name')}</td>  
                        <td>{i.get('passed cases')}</td>  
                        <td>{i.get('failed cases')}</td>  
                        <td>{i.get('task rating')}</td>  
                        <td>{i.get('failed test cases')}</td>  
                        <td></td>  
                        <td></td>  
                      </tr>  
                     """
            confluence_table += table
        # content = f'''
        #     <h2>Compute_release_ci_test_ddk2.0 {report_date}</h2>
        #     <ul>
        #         {''.join([f'<li>{task}</li>' for task in tasks])}
        #     </ul>
        #     '''
        with open('./ddk.log', 'r', encoding='utf-8') as f:
            log_str = f.read().split('------------------------------------------')
        upload_table = f"""
                <table>  
                     <tr>  
                        <th>test tasks</th>  
                        <th>passed cases</th>  
                        <th>failed cases</th>  
                        <th>passed rate'</th>  
                        <th>failed test cases</th>  
                        <th>jira</th>  
                        <th>solution</th>  
                      </tr>
                      {confluence_table}
                      <td>{log_str[-1]}</td>  
                      <td></td>  
                      <td></td>  
                      <td></td>  
                      <td></td>  
                      <td></td>  
                      <td></td>  
                      </table>"""
        # print(upload_table)
        parent_id = self.confluence.get_page_id(space="SWQA", title=f'{report_date}')
        if product == 'cts':
            self.confluence.create_page(
                parent_id=parent_id,
                space='SWQA',
                title=f'{report_date}_MUSA_cts',
                body=confluence_table)
        elif product == 'ddk':
            self.confluence.create_page(
                parent_id=parent_id,
                space='SWQA',
                title=f'{report_date}_DDK_2.0',
                body=upload_table)

    def push_message(self):
        pass

    def parse_log(self):
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


'Compute_release_ci_test_ddk2.0 结果记录'
if __name__ == '__main__':
    # Send_ding_report().make_build_daily()
    # Send_ding_report().update_confluence('cts')
    Send_ding_report().update_confluence('ddk')
    df = Send_ding_report().parse_log()
    # 导出到Excel
    df.to_excel("test_results.xlsx", index=False)
