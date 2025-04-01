import json
import os
import re
from datetime import datetime
import jenkins
import requests
from dotenv import load_dotenv

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
        s80_rs = []
        s3000_rs = []
        s4000_rs = []
        s5000_rs = []
        report_date = datetime.now().strftime("%Y-%m-%d")
        try:
            page_true = self.confluence.get_page_by_title(space="SWQA", title=f"{report_date}").get('id')
        except AttributeError:
            print('页面未创建')

        if not page_true:
            self.confluence.create_page(
                parent_id=242474903,
                space='SWQA',
                title=f'{report_date}',
                body='')
        tasks = []
        if product == 'ddk':
            with open('./ddk.log', 'r', encoding='utf-8') as f:
                out_rs = f.readlines()
                for i in out_rs:
                    rs = re.search(r'root:([a-z]{1}\d+.*)', i)
                    try:
                        tasks.append(rs.group(1))
                    except Exception:
                        continue
        elif product == 'cts':
            with open('./cts.log', 'r', encoding='utf-8') as f:
                out_rs = f.readlines()
                for i in out_rs:
                    rs = re.search(r'root:([a-z]{1}\d+.*)', i)
                    try:
                        tasks.append(rs.group(1))
                    except Exception:
                        continue
        for i in tasks:
            if i.strip().split('-')[0] == 's80':
                s80_rs.append(f'<li>{i}</li>')
            if i.strip().split('-')[0] == 's3000':
                s3000_rs.append(f'<li>{i}</li>')
            if i.strip().split('-')[0] == 's4000':
                s4000_rs.append(f'<li>{i}</li>')
            if i.strip().split('-')[0] == 's5000':
                s5000_rs.append(f'<li>{i}</li>')
        with open('data.json', 'r', encoding='utf-8') as f:
            rs = json.loads(f.read())
            s8_build_info = []
            s3000_build_info = []
            s4000_build_info = []
            s5000_build_info = []
            for i in rs:
                if i.get('branch_farm') == 'dailyFarm':
                    if i.get('gpu_type') == 's80':
                        s8_build_info.append(f'<li>Gpu type: {i.get('gpu_type')}</li>'
                                             f'<li>Branch farm: {i.get('branch_farm')}</li>'
                                             f'<li>Build commit_id: {i.get('build_commit_id')}</li>'
                                             f'<li>Build time: {i.get('build_time')}</li>'
                                             f'<li>Build url: <a href="{i.get('build_url')}">{i.get('build_url')}</a></li>'
                                             f'<li>Task status: {i.get('status')}</li>')
                    if i.get('gpu_type') == 's3000':
                        s3000_build_info.append(f'<li>Gpu type: {i.get('gpu_type')}</li>'
                                                f'<li>Branch farm: {i.get('branch_farm')}</li>'
                                                f'<li>Build commit_id: {i.get('build_commit_id')}</li>'
                                                f'<li>Build time: {i.get('build_time')}</li>'
                                                f'<li>Build url: <a href="{i.get('build_url')}">{i.get('build_url')}</a></li>'
                                                f'<li>Task status: {i.get('status')}</li>')
                    if i.get('gpu_type') == 's4000':
                        s4000_build_info.append(f'<li>Gpu type: {i.get('gpu_type')}</li>'
                                                f'<li>Branch farm: {i.get('branch_farm')}</li>'
                                                f'<li>Build commit_id: {i.get('build_commit_id')}</li>'
                                                f'<li>Build time: {i.get('build_time')}</li>'
                                                f'<li>Build url: <a href="{i.get('build_url')}">{i.get('build_url')}</a></li>'
                                                f'<li>Task status: {i.get('status')}</li>')
                    if i.get('gpu_type') == 's5000':
                        s5000_build_info.append(f'<li>Gpu type: {i.get('gpu_type')}</li>'
                                                f'<li>Branch farm: {i.get('branch_farm')}</li>'
                                                f'<li>Build commit_id: {i.get('build_commit_id')}</li>'
                                                f'<li>Build time: {i.get('build_time')}</li>'
                                                f'<li>Build url: <a href="{i.get('build_url')}">{i.get('build_url')}</a></li>'
                                                f'<li>Task status: {i.get('status')}</li>')
            confluence_table = f"""
                <table>
                  <colgroup>
                    <col style="width: 25%" />
                    <col style="width: 25%" />
                    <col style="width: 25%" />
                    <col style="width: 25%" />
                  </colgroup>
                  <tr>
                    <th>s80</th>
                    <th>s3000</th>
                    <th>s4000</th>
                    <th>s5000</th>
                  </tr>
                  <tr>
                    <td>{''.join(str(item) for item in s8_build_info)}</td>
                    <td>{''.join(str(item) for item in s3000_build_info)}</td>
                    <td>{''.join(str(item) for item in s4000_build_info)}</td>
                    <td>{''.join(str(item) for item in s5000_build_info)}</td>
                  </tr>
                  <tr>
                    <td>{''.join(str(item) for item in s80_rs)}</td>
                    <td>{''.join(str(item) for item in s3000_rs)}</td>
                    <td>{''.join(str(item) for item in s4000_rs)}</td>
                    <td>{''.join(str(item) for item in s5000_rs)}</td>
                  </tr>
                </table>
            """

            #
            # content = f'''
            #     <h2>Compute_release_ci_test_ddk2.0 {report_date}</h2>
            #     <ul>
            #         {''.join([f'<li>{task}</li>' for task in tasks])}
            #     </ul>
            #     '''

            parent_id = self.confluence.get_page_id(space="SWQA", title=f'{report_date}')
            if product == 'cts':
                self.confluence.create_page(
                    parent_id=parent_id,
                    space='SWQA',
                    title='MUSA_cts',
                    body=confluence_table)
            elif product == 'ddk':
                self.confluence.create_page(
                    parent_id=parent_id,
                    space='SWQA',
                    title='DDK 2.0',
                    body=confluence_table)

    def push_message(self):
        pass


# rs1 = ' '.join(str(item) for item in rs_list)
# print(rs1)
# msg = ''.join(
#     f"""\n- **Compute_release_ci_ddk2.0 task build info:**
#    \n- **pass task:** {self.alter_msg(rs[1], '')}
#     \n- **fail task:**  {(self.alter_msg(rs[0], ''))}
#      \n- **error task:**  {self.alter_msg(rs[2], '')}
#       \n- **noreport task:**      {self.alter_msg(rs[3], '')}""")
# err_rs = Send_ding_report().make_build_daily()
# webhook = "https://oapi.dingtalk.com/robot/send?access_token=a6610f68343a345c1b8b5d4cced57dbeb70a6783c9a18f96f85dad268fa05054"
# content = {
#     "msgtype": "markdown",
#     "markdown": {
#         "title": "#daily report",
#         "text": rs_msg},
#     "at": {
#         "atUserIds": ["1bb-qgn5shbiod"],
#         "isAtAll": False}
# }
# response = requests.post(url=webhook, json=content, verify=False)
#
# if response.json()['errmsg'] != "ok":
#     return response.text
# return response

'Compute_release_ci_test_ddk2.0 结果记录'
if __name__ == '__main__':
    Send_ding_report().make_build_daily()
    Send_ding_report().update_confluence('cts')
    Send_ding_report().update_confluence('ddk')
