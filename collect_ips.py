import requests
from bs4 import BeautifulSoup
import re
import logging
import subprocess
import os

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 克隆的本地 Git 仓库路径
LOCAL_REPO_PATH = "Worker_Vless"  # 替换为你的本地仓库路径

# 目标 URL 列表
urls = [
    'https://ip.164746.xyz',
    'https://api.uouin.com/cloudflare.html',
    'https://ip.164746.xyz/ipTop.html',
    'https://ip.164746.xyz/ipTop10.html',
    'https://raw.githubusercontent.com/tianshipapa/cfipcaiji/refs/heads/main/ip.txt',
    'https://addressesapi.090227.xyz/CloudFlareYes',
    'https://addressesapi.090227.xyz/ip.164746.xyz',
    'https://ipdb.api.030101.xyz/?type=bestcf&country=true',
    'https://ipdb.030101.xyz/api/bestcf.txt'
]

# 正则表达式匹配 IP 地址
ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

# 获取 IP 的国家代码
def get_ip_country(ip):
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('success', False):
            return data.get('country_code', 'UNKNOWN').upper()
        else:
            logging.warning(f"IP {ip} 查询失败：{data.get('message', '未知错误')}")
            return 'UNKNOWN'
    except requests.exceptions.RequestException as e:
        logging.error(f"获取 {ip} 国家信息失败: {e}")
        return 'UNKNOWN'

# 从 URL 提取 IP 地址
def extract_ips_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ip_matches = set()
        elements = soup.find_all(text=ip_pattern)
        for element in elements:
            ip_matches.update(ip_pattern.findall(element))
        if ip_matches:
            logging.info(f"从 {url} 提取到 {len(ip_matches)} 个唯一 IP")
            return ip_matches
        else:
            logging.info(f"未找到 IP 地址：{url}")
            return set()
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败 {url}: {e}")
        return set()

# 保存 IP 地址到本地 Git 仓库文件
def save_to_git_repo(ip_addresses, repo_path):
    file_path = os.path.join(repo_path, "ip.txt")
    try:
        with open(file_path, 'w') as file:
            for ip, country in ip_addresses:
                file.write(f"{ip}#{country}\n")
        logging.info(f"IP 地址已保存到仓库文件 {file_path}")
    except Exception as e:
        logging.error(f"保存到仓库文件失败：{e}")

# 提交并推送更改到 Git 仓库
def commit_and_push_changes(repo_path):
    try:
        # 切换到仓库目录
        os.chdir(repo_path)
        # 添加文件到 Git 暂存区
        subprocess.run(["git", "add", "ip.txt"], check=True)
        # 提交更改
        subprocess.run(["git", "commit", "-m", "Update IP list"], check=True)
        # 推送更改到远程仓库
        subprocess.run(["git", "push", "origin", "main"], check=True)
        logging.info("更改已成功提交并推送到远程仓库")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git 操作失败：{e}")
    except Exception as e:
        logging.error(f"推送更改时出错：{e}")

# 主程序
def main():
    if not os.path.exists(LOCAL_REPO_PATH):
        logging.error(f"本地仓库路径不存在：{LOCAL_REPO_PATH}")
        return

    ip_addresses = set()
    for url in urls:
        ip_matches = extract_ips_from_url(url)
        for ip in ip_matches:
            country = get_ip_country(ip)
            ip_addresses.add((ip, country))

    if ip_addresses:
        save_to_git_repo(ip_addresses, LOCAL_REPO_PATH)
        commit_and_push_changes(LOCAL_REPO_PATH)
    else:
        logging.info("没有提取到任何 IP 地址。")

if __name__ == "__main__":
    main()
