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
domainSet=['1-dispose','adder-IPC5', 'adder-IPC6' ,'blocks','bomb','bt', 'btc', 'cleaner', 'coins', 'comm', 'cornerr-sqr','corners_cube','cube-center', 'dispose', 'forest', 'grid_small_rnd', 'logistics', 'look-and-grab','new-dispose','new-push','new-ring','new-uts-cycle', 'new-uts-k', 'or-1-dispose', 'or-coins', 'or-dispose','or-new-push','or-push-to','push-to','raos_keys','retrieve','reward','ring','safe','sortnet','sqr-center', 'to-trash','uts-cycle','uts-k','uts-l','uts-r','sinkcw','wallcw']
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
    title = ['domain','cff_counter','','','','','','','']
    title1 = ['instance','Time','CTime','Len','Ite','OldFactNum','Fold/Uold','NowFactNum','Fnow/Unow']
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
        ite_len = 0
        rst = 0
        node_num = 0
        cc_time = 0.0

        f_cur=0
        u_cur=0
        f_old=0
        u_old=0

        now_ite=0
        for i in range(0,length):
            # print(data[length-i-1])
            TimeOutPat = r".*TimeOut\s*"
            LengthPat = r'plan length:\s*(?P<planLen>\d+)\s*'
            TimePat = r'now_time:\s*(?P<totalTime>-?\d+\.?\d*e?-?\d*?)\s*'
            itePat = r'.*iteration:\s*(?P<iteration>\d+)\s*'
            C_time = r'counter_time:(?P<c_time>-?\d+\.?\d*e?-?\d*?)\s'
            Nite = r'\s*第(?P<nowite>\d+)次迭代\s*'

            ERPat = r'.*ERROR\s*'
            PassPat = r'.*pass.*'
            OutPat = r'.*Out of Memory.*'
            NoPlanPat = r'.*No plan found.*'
            
            Fold = r'Fold:\s*(?P<fold>\d+)\s*.*'
            Uold = r'.*Uold:\s*(?P<uold>\d+)\s*'
            Fcur = r'Fcur:\s*(?P<fcur>\d+)\s*.*'
            Ucur = r'.*Ucur:\s*(?P<ucur>\d+)\s*'
            
            FO = re.match(Fold,data[length-i-1])
            if FO!=None:
                tmp = FO.groupdict()
                f_old = tmp['fold']
            UO = re.match(Uold,data[length-i-1])
            if UO!=None:
                tmp = UO.groupdict()
                u_old = tmp['uold']
            FC = re.match(Fcur,data[length-i-1])
            if FC!=None:
                tmp = FC.groupdict()
                f_cur = tmp['fcur']
            UC = re.match(Ucur,data[length-i-1])
            if UC!=None:
                tmp = UC.groupdict()
                u_cur = tmp['ucur']

            L = re.match(LengthPat,data[length-i-1])
            if(L!=None):
                flag = flag | 1
                tmp = L.groupdict()
                p_len = tmp['planLen']
            Ct = re.match(C_time,data[length-i-1])
            if Ct!=None:
                tmp = Ct.groupdict()
                cc_time = tmp['c_time']
            Ite= re.match(itePat,data[length-i-1])
            if Ite!=None:
                tmp = Ite.groupdict()
                ite_len = tmp['iteration']
            T = re.match(TimePat,data[length-i-1])
            if(T!=None):
                flag = flag | 2
                tmp = T.groupdict()
                t_time = tmp['totalTime']
            NITE = re.match(Nite,data[length-i-1])
            if(NITE!=None):
                tmp = NITE.groupdict()
                now_ite = tmp['nowite']
                break

            NP = re.match(NoPlanPat,data[length-i-1])
            if NP!=None:
                flag = 0

            O = re.match(TimeOutPat,data[length-i-1])
            if O!=None:
                flag = flag | 4

            M = re.match(OutPat,data[length-i-1])
            if M!=None:
                flag = flag | 8

            P = re.match(PassPat,data[length-i-1])
            if P!=None:
                flag = flag |16

            E = re.match(ERPat,data[length-i-1])
            if E!=None:
                flag = flag |32
            
        # 能找到规划
        if flag ==3:
            work_sheet.write(now_row,1,format(float(t_time),'.4f'))
            work_sheet.write(now_row,2,format(float(cc_time),'.4f'))
            work_sheet.write(now_row,3,p_len)
            work_sheet.write(now_row,4,ite_len)
            work_sheet.write(now_row,5,int(f_old)+int(u_old))
            if int(u_cur)==0:
                work_sheet.write(now_row,6,'u_old=0')
            else:
                work_sheet.write(now_row,6,format(float(float(f_old)/float(u_old)),'.4f'))
            work_sheet.write(now_row,7,int(f_cur)+int(u_cur))
            if int(u_cur)==0:
                work_sheet.write(now_row,8,'u_cur=0')
            else:
                work_sheet.write(now_row,8,format(float(float(f_cur)/float(u_cur)),'.4f'))
            now_row = now_row+1
        # 未找到规划
        if flag ==0 or flag ==2:
            work_sheet.write(now_row,1,'NP')
            now_row = now_row+1
        # 没有匹配值，表示越界
        elif flag ==10 or flag ==8:
            work_sheet.write(now_row,2,'OM')
            work_sheet.write(now_row,1,format(float(t_time),'.4f'))
            work_sheet.write(now_row,4,int(now_ite))
            now_row = now_row+1
        # 超时
        elif flag ==6 or flag ==4:
            work_sheet.write(now_row,1,'TO')
            work_sheet.write(now_row,4,int(now_ite))
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
    det = work_book.save('cff_counter.xls')
    print('excel文件创建成功')
    
