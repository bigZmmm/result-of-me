#!/usr/bin/python3.8
from asyncore import write
from base64 import encode
from cgi import test
from ctypes import sizeof
from enum import Flag
from operator import mod
import os
import sys
from xml.dom import NoModificationAllowedErr
import xlwt
import re
import nums_from_string
# domainSet=['wallcw']
domainSet=['1-dispose',  'blocks','bomb','bt', 'btc', 'cleaner', 'coins', 'comm', 'cornerr-sqr','corners_cube','cube-center', 'dispose', 'forest', 'grid_small_rnd', 'logistics', 'look-and-grab','new-dispose','new-push','new-ring','new-uts-cycle', 'new-uts-k', 'or-1-dispose', 'or-coins', 'or-dispose','or-new-push','or-push-to','push-to','raos_keys','retrieve','reward','ring','safe','sortnet','sqr-center', 'to-trash','uts-cycle','uts-k','uts-l','uts-r','sinkcw','wallcw']
# 表示当前的行

work_book=None
work_sheet=None
now_row=0
'''
    获取目录所有文件夹及内容
'''
mp={}
def file_name(file_path):
    for root, dirs, files in os.walk(file_path):
        mp[root]=files
        mp[root].sort(key = lambda x:(len(x), x)) # record the file in the root

def create_excel():
    global work_book
    global work_sheet
    global now_row
    work_book = xlwt.Workbook(encoding = 'utf-8')
    work_sheet = work_book.add_sheet('Conformant_det',cell_overwrite_ok=True)
    now_row =0
    title = ['domain','cff','','']
    title1 = ['instance','Time','Len','iteration']
    for i in range(len(title)):
        work_sheet.write(now_row,i,title[i])
        work_sheet.write(now_row+1,i,title1[i])
    now_row = now_row+2
# 将数据写入
def read_txt(path:str):
    global work_sheet
    global now_row
    with open(path, 'r', encoding='utf-8') as f:
        data = f.readlines()
        # print(data)
        length = len(data)
        flag = 0
        # 倒着获取值，直到得到所有
        t_time = 0.0
        p_len = 0
        ex_len = 0
        rst = 0
        node_num = 0
        cc_time = 0.0
        for i in range(0,length):
            # print(data[length-i-1])
            TimeOutPat = r".*TimeOut\s*"
            LengthPat = r'plan length:\s*(?P<planLen>\d+)\s*'
            TimePat = r'now_time:\s*(?P<totalTime>-?\d+\.?\d*e?-?\d*?)\s*'
            ERPat = r'.*ERROR\s*'
            PassPat = r'.*pass.*'
            OutPat = r'.*Out of Memory.*'
            ExoandPat = r'.*iteration:\s*(?P<expandNum>\d+)\s*'
            NoPlanPat = r'.*No plan found.*'
            RSTPat = r'Random sample times =\s*(?P<RSTNum>\d+)\s*'
            ExNodePat = r'ExpandNode =\s*(?P<nodeNum>\d+)\s*'
            C_time = r'Counter sample time = (?P<c_time>-?\d+\.?\d*e?-?\d*?) sec'
            Ct = re.match(C_time,data[length-i-1])
            if Ct!=None:
                tmp = Ct.groupdict()
                cc_time = tmp['c_time']
            Node = re.match(ExNodePat,data[length-i-1])
            if Node!=None:
                tmp = Node.groupdict()
                node_num = tmp['nodeNum']
            NP = re.match(NoPlanPat,data[length-i-1])
            if NP!=None:
                flag = 0
                break
            RST = re.match(RSTPat,data[length-i-1])
            if(RST!=None):
                tmp = RST.groupdict()
                rst = tmp['RSTNum']
            O = re.match(TimeOutPat,data[length-i-1])
            if O!=None:
                flag = flag | 4
                break
            M = re.match(OutPat,data[length-i-1])
            if M!=None:
                flag = flag | 8
                break
            L = re.match(LengthPat,data[length-i-1])
            if(L!=None):
                flag = flag | 1
                tmp = L.groupdict()
                p_len = tmp['planLen']
            T = re.match(TimePat,data[length-i-1])
            if(T!=None):
                flag = flag | 2
                tmp = T.groupdict()
                t_time = tmp['totalTime']
            P = re.match(PassPat,data[length-i-1])
            if P!=None:
                flag = flag |16
                break
            E = re.match(ERPat,data[length-i-1])
            if E!=None:
                flag = flag |32
                break
            Pand= re.match(ExoandPat,data[length-i-1])
            if Pand!=None:
                tmp = Pand.groupdict()
                ex_len = tmp['expandNum']
        # 能找到规划
        if flag ==3:
            work_sheet.write(now_row,1,format(float(t_time),'.4f'))
            work_sheet.write(now_row,2,p_len)
            work_sheet.write(now_row,3,ex_len)
            now_row = now_row+1
        # 未找到规划
        if flag ==0 or flag ==2:
            work_sheet.write(now_row,1,'NP')
            now_row = now_row+1
        # 没有匹配值，表示越界
        elif flag ==10 or flag ==8:
            work_sheet.write(now_row,1,'OM')
            work_sheet.write(now_row,2,format(float(t_time),'.4f'))
            now_row = now_row+1
        # 超时
        elif flag ==6 or flag ==4:
            work_sheet.write(now_row,1,'TO')
            now_row = now_row+1
        # 错误
        elif flag ==32:
            work_sheet.write(now_row,1,'NA')
            now_row = now_row+1
        # 跳过
        elif flag ==16:
            work_sheet.write(now_row,1,'-')
            now_row = now_row+1

def red_dir():
    global work_sheet
    global now_row
    for dir in domainSet:
        dir_name = './'+dir+'_res'
        print('now analazing file is: '+dir+'...')
        dirs = mp[dir_name]
        title = dir+'({})'.format(len(dirs))
        work_sheet.write(now_row,0,title)

        now_row = now_row + 1
        
        # 每个大类型要加一个大标题
        for result in dirs:
            # 提取文件名中的数字，加成一个小标题
            nums = nums_from_string.get_nums(result)
            instance_name = ''
            for i in range(len(nums)):
                instance_name +=str(abs(nums[i]))
                if i!=len(nums)-1:
                    instance_name += '-'
            file_dir = dir_name+'/'+result
            work_sheet.write(now_row,0,instance_name)
            # print(instance_name)
            read_txt(file_dir)

if __name__ == "__main__":
    file_name('./')
    create_excel()
    red_dir()
    det = work_book.save('cff_old.xls')
    print('excel文件创建成功')
    
