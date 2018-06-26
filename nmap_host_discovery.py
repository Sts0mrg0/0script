#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/6 14:20
# @Author  : BLKStone
# @Site    : http://blkstone.github.io
# @File    : host_dicovery.py
# @Software: PyCharm

import sys
import time

# openpyxl
from openpyxl import Workbook

# libnmap
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException


# 测试环境的 Nmap 版本为 7.6
# 在部署过程中，
# 曾经遇到过 7.6 与 5.5 的 Nmap 扫描结果不一致的问题

# print scan results from a nmap report
def print_scan(nmap_report):
    print("Starting Nmap {0} ( http://nmap.org ) at {1}".format(
        nmap_report.version,
        nmap_report.started))

    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        print("Nmap scan report for {0} ({1})".format(
            tmp_host,
            host.address))
        print("Host is {0}.".format(host.status))
        print("  PORT     STATE         SERVICE")

        for serv in host.services:
            pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(
                    str(serv.port),
                    serv.protocol,
                    serv.state,
                    serv.service,)
            if len(serv.banner):
                pserv += " ({0})".format(serv.banner)
            print(pserv)
    print(nmap_report.summary)


# 从文件读取扫描目标
def read_targets(path):
    targets = []
    with open(path, 'r') as f:
        for ele in f.readlines():
            targets.append(ele.strip())
    # print(targets)
    return targets


# 常规 主机发现 扫描
def default_scan(target_path):

    # config parameters
    sleep_interval = 10

    # start scan
    target_list = read_targets(target_path)

    # heavy scan
    # nmap_proc = NmapProcess(targets=target_list, options="-sS -n -PE -PP -PM -PO -PS21,22,23,25,80,113,31339 -PA80,"
    #                                                               "113,443,10042 -O -T4 -p-")
    # light scan
    nmap_proc = NmapProcess(targets=target_list, options="-PE -PP -PM -PO -PS21,22,23,25,80,113,31339 -PA80,"
                                                         "113,443,10042 -O -T4")

    # debug info
    print("scan target:")
    print(target_list)
    print("command:")
    print(nmap_proc.command)

    nmap_proc.run_background()
    while nmap_proc.is_running():
        print("Nmap Scan running: ETC: {0} DONE: {1}%".format(nmap_proc.etc,
                                                              nmap_proc.progress))
        time.sleep(sleep_interval)

    print("rc: {0} output: {1}".format(nmap_proc.rc, nmap_proc.summary))

    # save to file
    time_label = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open('nmap_scan_'+time_label+'.xml', 'w') as f:
        f.write(nmap_proc.stdout)
    f.close()

    try:
        nmap_report = NmapParser.parse(nmap_proc.stdout)
    except NmapParserException as e:
        print("Exception raised while parsing scan: {0}".format(e.msg))
        return None

    print_scan(nmap_report)

    return nmap_report


# 将结果导出为 Excel
def xlsx_output(nmap_report, output_path='default.xlsx'):

    print("Starting Nmap {0} ( http://nmap.org ) at {1}".format(
        nmap_report.version,
        nmap_report.started))

    wb_write = Workbook()
    ws_write = wb_write.active

    idx = 1
    header = ['No.1', 'host_name', 'host_address', 'host_status', 'port', 'protocol', 'service', 'state', 'reason',
              'reason-ttl', 'banner', 'OS']
    ws_write.append(header)

    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        if len(host.os_match_probabilities()) == 0:
            os_name = 'Unknown'
        else:
            # 长度超了
            os_name = host.os_match_probabilities()[0].name[0:49]

        if host.status == 'down':
            row_info = [idx, tmp_host, host.address, host.status, '-', '-', '-', '-',
                        '-', '-', '-', os_name]
            ws_write.append(row_info)
            idx += 1

        if len(host.services) == 0 and host.status == 'up':
            row_info = [idx, tmp_host, host.address, host.status, '-', '-', '-', '-',
                        '-', '-', '-', os_name]
            ws_write.append(row_info)
            idx += 1

        for serv in host.services:

            row_info = [idx, tmp_host, host.address, host.status, serv.port, serv.protocol, serv.service, serv.state,
                        serv.reason, serv.reason_ttl, serv.banner, os_name]
            ws_write.append(row_info)
            idx += 1

    if output_path == 'default.xlsx':
        output_path = 'nmap-scan-' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.xlsx'
    wb_write.save(output_path)


def xml2xlsx(xml_path):
    nmap_report = NmapParser.parse_fromfile(xml_path)
    xlsx_output(nmap_report)


#######################################################################################################################
# 以下为测试函数
#######################################################################################################################

# 接下来可以考虑一下 和 ndiff, DNmap (分布式) 等的整合

# 解析 nmap 输出的 xml 文件
def parse_xml_from_file(xml_path):
    # xml_path = 'C:\\Users\\Jack\\Desktop\\Nmap_Test_Scan\\c.xml'
    nmap_report = NmapParser.parse_fromfile(xml_path, incomplete=True)
    print_scan(nmap_report)
    return nmap_report


def ascan():
    target_path = 'D:\\pydev\\nmap_automation\\pythontest\\config\\scan_target_1.txt'
    report = default_scan(target_path)
    xlsx_output(report)


def areport():
    print("parsing report...")
    xml_path = "D:\\pydev\\nmap_automation\\pythontest\\nmap_result2018_06_07_2246.xml"
    xml2xlsx(xml_path)


if __name__ == '__main__':

    # python host_discovery.py scan scan_target_1.txt
    # python host_discovery.py parse nmap_scan.xml

    mode = sys.argv[1]
    target_path = sys.argv[2]
    
    print("mode: " + mode)
    print(target_path)
    
    if mode == 'scan':
        report = default_scan(target_path)
        xlsx_output(report)
    elif mode == 'parse':
        xml2xlsx(target_path)
    else:
        print("error mdoe")
