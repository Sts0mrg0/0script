#coding=utf-8

import re
import csv
import pymysql
import os
import argparse
from bs4 import BeautifulSoup

def main():
    path = 'D:/Users/choffer/Desktop/code/test/www.himaster.com.tw'
    for rootpath,dirspath,filespath in os.walk(path):
        for f in filespath:
            filepath = os.path.join(rootpath,f).replace('\\','/')
            # print(filepath)
            try:
                caidao(filepath)
            except Exception as identifier:
                pass
            

def caidao(filepath):
    # html_name = '''DormSupplier.html'''
    soup = BeautifulSoup(open(filepath, 'rb'), 'lxml')
    html_text = str(soup)
    parse_title = '''<tr class="th">(.*?)<tr>'''
    parse_content = '''<tr style="">(.*?)<tr>'''
    parse_text = '''<td>(.*?)</td>'''

    html_name = filepath.split('/')
    html_name = html_name[-2]+'_'+html_name[-1].replace('.','_')
    print(html_name)
    title_content = re2parser(parse_title, html_text)
    # 返回的title_content是一个列表
    title_text = re2parser(parse_text, title_content[0])
    mysql2table(title_text, html_name)
    # 往表里写数据
    html_content = re2parser(parse_content, html_text)
    mysql2text(html_content, parse_text, html_name, title_text)

# 正则解析出文本
def re2parser(parse_re, html_text):
    parser = re.compile(parse_re, re.S)
    text = re.findall(parser, html_text)
    return text

# 生成csv
def csv2write(parameter_list):
    with open('test.csv', 'a+', encoding='utf-8', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(parameter_list)
        csvfile.close()

# 生成表
def mysql2table(title_text, html_name):
    sql = ''
    for a in title_text:
        sql = sql+a+' varchar(255), '
    table_title = ' ('+sql[:-2]+')'
    sql = 'CREATE TABLE '+html_name+table_title
    try:
        db = pymysql.connect("localhost","root","root","test",use_unicode=True, charset='utf8')
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS "+html_name)
        cursor.execute(sql)
    except Exception as identifier:
        print(identifier)
    print('连接数据库，生成表：'+html_name)
    print(sql+'\n')
    db.close()

# 往表里写数据
def mysql2text(html_content, parse_text, html_name, title_text):
    # 打开数据库连接
    db = pymysql.connect("localhost","root","root","test",use_unicode=True, charset='utf8')
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()
    table_columns = ''
    for c in title_text:
        table_columns = table_columns+c+','
    for a in html_content:
        content_text = re2parser(parse_text, a)
        # SQL 插入语句
        sql = ''
        for b in content_text:
            if b:
                sql = sql+'"'+b.replace(',','_')+'", '
            else:
                sql = sql+'"'+b.replace(',','_')+'unknown", '
        #INSERT INTO DormSupplier (SupplierId,Sup_Name,Sup_ID,Sup_Boss,Sup_Pern,Sup_Tel,Sup_Mobile,Sup_Mobile2,Sup_Fax,Sup_Address,Category,Area,MultiCategory,Payment,ProvideId,Product,Photo,ProvideUnitNo) VALUES (31, '賀立水電工程', 45745862, '王賀立', '王賀立', 04-26868349, 0927567923, 'unknown', 04-26871288, '台中市大甲區南北三路36-4號', '''unknown''', 2, 0-1-2-10-11-12-15-84-85-87, 2, 1272, 'unknown', 'unknown', 03)
        sql = 'INSERT INTO '+html_name+' ('+table_columns[:-1]+') VALUES ('+sql[:-2]+')'
        print('往表：'+html_name+'里面插入数据')
        print(sql)
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except Exception as e:
            print(e)
            # 如果发生错误则回滚
            db.rollback()
    # 关闭数据库连接
    db.close()

if __name__ == '__main__':
    main()