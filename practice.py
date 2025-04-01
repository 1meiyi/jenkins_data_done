import json
import os
import re
from datetime import datetime
import jenkins
import requests
from dotenv import load_dotenv
from atlassian import Confluence

load_dotenv('./yi.mei.env')
confluence_url = os.getenv("CONFLUENCE_URL")
confluence_name = os.getenv("CONFLUENCE_USERNAME")
confluence_token = os.getenv("CONFLUENCE_TOKEN")
print(confluence_url, confluence_name, confluence_token)
confluence = Confluence(
    url=confluence_url,
    username=confluence_name,
    password=confluence_token,
    cloud=False)

parent_id = confluence.get_page_id(space="SWQA", title='Compute_release_ci_test_ddk2.0 结果记录')
# tasks = []
# with open('./cts.log', 'r', encoding='utf-8') as f:
#     out_rs = f.readlines()
#     for i in out_rs:
#         rs = re.search(r'root:([a-z]{1}\d+.*)', i)
#         try:
#             tasks.append(rs.group(1))
#         except Exception:
#             continue
# report_date = datetime.now().strftime("%Y-%m-%d")
# content = f'''
# <h2>Compute_release_ci_test_ddk2.0 {report_date}</h2>
# <ul>
#     {''.join([f'<li>{task}</li>' for task in tasks])}
# </ul>
# '''
# confluence.create_page(
#     space='SWQA',
#     title=f'Compute_release_ci_test_ddk2.0 结果记录',
#     body=content
# )
# confluence.update_page(
#     page_id=parent_id,
#     title=f'Compute_release_ci_test_ddk2.0 结果记录',
#     body=content
# )
#
# spaces = confluence.get_all_spaces()
# page_title = "Test"
# page_id = confluence.get_page_id('SWQA', page_title)

print(parent_id)
