import requests
from bs4 import BeautifulSoup
import re

# 目标URL列表
urls = ['https://cf.090227.xyz', 'https://ip.164746.xyz',
        'https://api.uouin.com/cloudflare.html',
        'https://ip.164746.xyz/ipTop.html',
        'https://raw.githubusercontent.com/tianshipapa/cfipcaiji/refs/heads/main/ip.txt',
        'https://addressesapi.090227.xyz/CloudFlareYes',
        'https://addressesapi.090227.xyz/ip.164746.xyz',
        'https://ipdb.api.030101.xyz/?type=bestcf&country=true',
        'https://ipdb.030101.xyz/api/bestcf.txt'
       ]

# 正则表达式匹配IP地址
ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

# 获取IP的国家简称
def get_ip_country(ip):
    try:
        # 使用 ipwhois 查询国家代码
        response = requests.get(f"https://ipwhois.app/json/{ip}")
        data = response.json()

        # 调试输出：打印 IP 查询的返回数据
        print(f"IP {ip} 查询返回数据: {data}")

        # 检查返回数据并获取国家代码
        if data.get('success', False):
            return data.get('country_code', 'unknown').lower()
        else:
            print(f"IP {ip} 查询失败：{data.get('message', '未知错误')}")
            return 'unknown'
    except Exception as e:
        print(f"获取 {ip} 国家信息失败: {e}")
        return 'unknown'

# 提取IP地址
def extract_ips_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 调试输出：网页内容前500字符
        print(f"抓取的HTML内容 (前500字符)：\n{response.text[:500]}")

        # 直接从网页中匹配IP地址
        ip_matches = set()
        elements = soup.find_all(text=re.compile(ip_pattern))
        for element in elements:
            ip_matches.update(re.findall(ip_pattern, element))

        if ip_matches:
            print(f"从 {url} 提取到 {len(ip_matches)} 个唯一IP")
            return ip_matches
        else:
            print(f"未找到IP地址：{url}")
            return set()
    except Exception as e:
        print(f"请求失败 {url}: {e}")
        return set()

# 主程序
def main():
    ip_addresses = set()
    for url in urls:
        ip_addresses.update(extract_ips_from_url(url))

    if ip_addresses:
        with open('ip.txt', 'w') as file:
            for ip in ip_addresses:
                country = get_ip_country(ip)
                file.write(f"{ip}#{country}\n")
        print("IP地址已保存到 ip.txt 文件中。")
    else:
        print("没有提取到任何IP地址。")

if __name__ == "__main__":
    main()
