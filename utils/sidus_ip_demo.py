import requests
import boto3
import re
import os
import datetime


# 　获取本地ip
def get_internet_ip():
    res = requests.get('http://www.3322.org/dyndns/getip')
    if res.status_code == 200:
        ip = re.sub(r'\s+', '', res.text)
    else:
        res = requests.get('http://myip.ipip.net')
        ip_ = re.findall(r'\d+\.\d+\.\d+\.\d+', res.text)
        if ip_:
            ip = ip_[0]

    return ip + '/32'


# 取消ip规则
def revoke_ip_rule(ec2, group_id, security_ip, security_port):
    pass


# 添加ip规则
def set_ip_rule(ec2, group_id, security_port):
    pass


if __name__ == '__main__':
    AWS_ACCESS_KEY_ID = 'AKIAJOR5WTDFS5OIKDXA'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_S3_REGION_NAME = 'us-west-1'

    client = boto3.client('ec2',
                          region_name=AWS_S3_REGION_NAME,  # 安全组所属区域
                          aws_access_key_id=AWS_ACCESS_KEY_ID,  # IAM账号id
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)  # IAM账号key
    ec2_group_id = 'sg-0e02a4124915d79c2'
    rds_group_id = 'sg-0f0b779767ac7bad7'

    ec2_port = 22
    rds_port = 3306
    rq_port = 15672

    res = client.describe_security_groups(GroupIds=[ec2_group_id,rds_group_id])

    r_ip = []
    print(res['SecurityGroups'][0]['IpPermissions'])
    # for item in res['SecurityGroups'][0]['IpPermissions']:
    #
    #     for iprange in item['IpRanges']:
    #         r_ip.append(iprange['CidrIp'])
    #
    # now = datetime.datetime.now().strftime('%m-%d_%H:%M:%S')
    # my_ip = get_internet_ip()
    #
    # if my_ip not in r_ip:
    #     rds_set = client.authorize_security_group_ingress(
    #         GroupId=rds_group_id,
    #         IpPermissions=[{
    #             'IpProtocol': 'tcp',
    #             'FromPort': rds_port,
    #             'ToPort': rds_port,
    #             'IpRanges': [{'CidrIp': my_ip, 'Description': now}]
    #         }]
    #     )
    #
    #     ec2_set = client.authorize_security_group_ingress(
    #         GroupId=ec2_group_id,
    #         IpPermissions=[{
    #             'IpProtocol': 'tcp',
    #             'FromPort': ec2_port,
    #             'ToPort': ec2_port,
    #             'IpRanges': [{'CidrIp': my_ip, 'Description': now}]
    #             },
    #             {
    #                 'IpProtocol': 'tcp',
    #                 'FromPort': rq_port,
    #                 'ToPort': rq_port,
    #                 'IpRanges': [{'CidrIp': my_ip, 'Description': now}]
    #             }
    #         ]
    #     )
    #     print('success')

