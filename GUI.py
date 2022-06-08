# -*- coding = utf-8 -*-
# @Time : 2022/6/5 20:18
# @Author : SBP
# @File : GUI.py
# @Software : PyCharm

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import cv2
import torch
from PIL import Image, ImageTk
import threading
import os
import mymtcnnlib.utils
import mymtcnnlib.detector
from threading import Lock
from copy import deepcopy
import sqlite3
import time
from myreconglib import compare

capture_flag = 0
person_num = 0
lock1 = Lock()  # 线程锁
lock2 = Lock()
lock3 = Lock()
# 数据库初始化
con = sqlite3.connect('./datas/logins/db.sqlite3', check_same_thread=False)  # 运行线程运行
cur = con.cursor()


class Frame_left_up:
    def __init__(self, root):
        self.cap = None
        self.start_flag = 0
        # self.interupt = 0  # 截取中断
        self.mainwindow = tk.LabelFrame(root, text='Camara', font=('', 40, 'bold'))
        self.mainwindow.place(relx=0, rely=0, relwidth=0.5, relheight=0.65)
        self.camara = tk.Label(self.mainwindow)
        # self.camara.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)
        self.camara.pack()
        self.button_start = tk.Button(self.mainwindow, text='Start', font=('', 15, 'bold'), width=15, height=1,
                                      command=self.start).place(relx=0.1, rely=0.88, relwidth=0.2, relheight=0.1)

        self.button_cut = tk.Button(self.mainwindow, text='Cut', font=('', 15, 'bold'), width=15, height=1,
                                    command=self.cut).place(relx=0.7, rely=0.88, relwidth=0.2, relheight=0.1)

    def start(self):
        # 开启摄像头
        # Thread 1
        if self.start_flag == 0:
            self.cap = cv2.VideoCapture(0)
            self.start_flag = 1
            p1 = threading.Thread(target=self.__start__)
            p1.start()
        else:
            pass

    def __start__(self):
        delayflag = None
        while True:
            _, frame = self.cap.read()
            # print(frame)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转成Image类
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camara.configure(image=imgtk)
            delayflag = imgtk  # 指针指向imgtk,延迟销毁

    def cut(self):
        # Thread 2
        p2 = threading.Thread(target=self.__cut__)
        p2.start()

    def __cut__(self):
        if self.start_flag == 0:
            # means 摄像头还未开
            messagebox.showerror(title='Error', message='Please Start First!')
            pass
        else:
            _, frame = self.cap.read()
            print('11111')
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            img.save('./datas/downloads/download.png')
            # 捕捉图像
            detector = detector_mtcnn()
            detector.capture()
            global capture_flag
            lock1.acquire()
            capture_flag = 1
            lock1.release()
            # Frame_right_up(root)
            messagebox.showinfo(title='Success', message='Successfully Capture the Picture!')


class Frame_right_up:
    def __init__(self, root):
        self.mainwindow = tk.LabelFrame(root, text='Comparation', font=('', 40, 'bold'))
        self.mainwindow.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.65)
        self.leftlabel = tk.Label(self.mainwindow, text='Capture Image', font=('', 20, 'bold')).place(relx=0, rely=0,
                                                                                                      relwidth=0.5,
                                                                                                      relheight=0.1)
        self.rightlabel = tk.Label(self.mainwindow, text='Database Image', font=('', 20, 'bold')).place(relx=0.5,
                                                                                                        rely=0,
                                                                                                        relwidth=0.5,
                                                                                                        relheight=0.1)
        self.xscrollbar1 = tk.Scrollbar(self.mainwindow, orient=tk.HORIZONTAL)
        self.xscrollbar1.place(relx=0, rely=0.6, relwidth=0.5, relheight=0.03)
        self.leftFrame = tk.Canvas(self.mainwindow)
        self.leftFrame.config(xscrollcommand=self.xscrollbar1.set)
        self.leftFrame.config(scrollregion=(0, 0, 800, 800))

        self.leftFrame.place(relx=0, rely=0.1, relwidth=0.5, relheight=0.5)

        self.xscrollbar1.config(command=self.leftFrame.xview)
        # self.xscrollbar1.config(command=self.leftFrame.xview)
        # self.leftFrame.images = []
        self.rightFrame = tk.Canvas(self.mainwindow)
        self.rightFrame.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=0.5)

        self.button_show = tk.Button(self.mainwindow, text='Show', font=('', 15, 'bold'), width=15, height=1,
                                     command=self.show_capture_img).place(relx=0.15, rely=0.85, relwidth=0.2,
                                                                          relheight=0.1)

        self.labelin = tk.Label(self.mainwindow, text='Input Name:', font=('', 15, 'bold')).place(relx=0.52, rely=0.65,
                                                                                                  relwidth=0.2,
                                                                                                  relheight=0.1)

        self.inputbox = tk.Entry(self.mainwindow)
        self.inputbox.insert(0, 'insert your name')
        self.inputbox.place(relx=0.72, rely=0.68, relwidth=0.2, relheight=0.05)

        self.button_login = tk.Button(self.mainwindow, text='Upload', font=('', 15, 'bold'), width=15, height=1,
                                      command=self.upload).place(relx=0.65, rely=0.85, relwidth=0.2, relheight=0.1)

    def show_capture_img(self):
        global capture_flag
        lock1.acquire()
        capture_flag_in = deepcopy(capture_flag)
        lock1.release()
        if capture_flag_in == 1:
            p3 = threading.Thread(target=self.__show_capture_img__, )
            p3.start()
        else:
            messagebox.showinfo(title='Wait', message='Please Wait!')

    def __show_capture_img__(self):
        global person_num
        print(person_num)
        self.leftFrame.images = []
        for i in range(person_num):
            img = Image.open('./datas/downloads/persons/person' + str(i) + '.png')
            w, h = img.size
            print(w, h)
            # img.show()
            # frame_img = tk.Canvas(self.leftFrame)
            # frame_img.place(relx=0 + i * 0.75, rely=0, relwidth=0.75, relheight=0.95)
            # frame_img.pack()
            imgtk = ImageTk.PhotoImage(image=img)
            self.leftFrame.create_image((0 + i * 180, 0), anchor=tk.NW, image=imgtk)
            self.leftFrame.images.append(imgtk)  # 延迟销毁

    def upload(self):
        input_name = self.inputbox.get()
        if input_name == 'insert your name' or input_name == '':
            messagebox.showerror(title='Error', message='please insert your name First')
        else:
            p4 = threading.Thread(target=self.__upload__, args=(input_name,))
            p4.start()

    def __upload__(self, input_name):
        picpath = selectPath()
        # print(input_name, picpath)
        # !!!!!!!!!!!!!!!!!!!!!!!! 插入第二层网络
        # 插入数据库 ########### need
        sqlfind = 'SELECT * FROM Persons WHERE name=\'{}\''.format(input_name)
        cur.execute(sqlfind)
        res = cur.fetchall()
        if len(res) == 0:
            # 数据库中没有 => 插入语句
            sql = 'insert into Persons(name, picpath, optime) values (\'{}\',\'{}\',\'{}\')'.format(input_name, picpath,
                                                                                                    time.strftime(
                                                                                                        '%Y%m%d%H%M%S'))
        else:
            # 数据库中存在 => 更新语句
            sql = 'UPDATE Persons SET picpath=\'{}\',optime=\'{}\' WHERE name=\'{}\''.format(picpath, time.strftime(
                '%Y%m%d%H%M%S'), input_name)
        # 执行数据库指令
        cur.execute(sql)
        con.commit()
        image = Image.open(picpath)
        imgtk = ImageTk.PhotoImage(image=image)
        self.rightFrame.create_image((0, 10), anchor=tk.NW, image=imgtk)
        self.rightFrame.img = imgtk
        messagebox.showinfo(title='Success', message='Successfully change Sql')


class Frame_down:
    def __init__(self, root):
        self.mainwindow = tk.Frame(root)
        self.path_capture_dir = './datas/downloads/persons/'
        self.recognitions = []  # need thread lock
        self.findings = []  # need thread lock
        self.mainwindow.place(relx=0, rely=0.65, relwidth=1, relheight=0.35)
        self.button_compare = tk.Button(self.mainwindow, text='Compare', font=('', 15, 'bold'), width=15, height=1,
                                        command=self.compare).place(relx=0.1, rely=0.25, relwidth=0.1, relheight=0.15)
        self.button_find = tk.Button(self.mainwindow, text='Find', font=('', 15, 'bold'), width=15, height=1,
                                     command=self.find).place(relx=0.1, rely=0.55, relwidth=0.1, relheight=0.15)
        self.sbar1 = tk.Scrollbar(self.mainwindow)
        self.sbar1.place(relx=0.6, rely=0.1, relwidth=0.02, relheight=0.8)
        self.sbar2 = tk.Scrollbar(self.mainwindow, orient=tk.HORIZONTAL)
        self.sbar2.place(relx=0.3, rely=0.9, relwidth=0.3, relheight=0.05)
        self.mylist = tk.Listbox(self.mainwindow, xscrollcommand=self.sbar2.set, yscrollcommand=self.sbar1.set,
                                 font=(20))
        self.mylist.place(relx=0.3, rely=0.1, relwidth=0.3, relheight=0.8)
        self.sbar1.config(command=self.mylist.yview)
        self.sbar2.config(command=self.mylist.xview)

        self.xscrollbar = tk.Scrollbar(self.mainwindow, orient=tk.HORIZONTAL)
        self.xscrollbar.place(relx=0.63, rely=0.9, relwidth=0.37, relheight=0.05)
        self.right_imgs = tk.Canvas(self.mainwindow)
        self.right_imgs.config(xscrollcommand=self.xscrollbar.set)
        self.right_imgs.config(scrollregion=(0, 0, 800, 800))
        self.right_imgs.place(relx=0.63, rely=0.1, relwidth=0.37, relheight=0.8)
        self.xscrollbar.config(command=self.right_imgs.xview)

    def compare(self):
        p5 = threading.Thread(target=self.__compare__, )
        p5.start()

    def __compare__(self):

        images_num = len(os.listdir(self.path_capture_dir))
        print('aaaaa')
        print(images_num)
        if images_num == 0:
            messagebox.showerror(title='Error', message='Please cut first')
        else:
            sql = 'SELECT * FROM Persons ORDER BY optime DESC LIMIT 1'
            cur.execute(sql)
            res = cur.fetchall()
            print(res)
            if len(res) == 0:
                messagebox.showerror(title='Error', message='there is no datas in SQL!')
            else:
                self.recognitions = []
                pic_path = res[0][2]
                img_sql = Image.open(pic_path)
                self.mylist.delete(0, tk.END)

                self.recognitions = []
                for i in range(images_num):
                    print('main:{}'.format(i))
                    path_cut = self.path_capture_dir + 'person' + str(i) + '.png'
                    img_cut = Image.open(path_cut)
                    bool_flag, distance = self.Net_base(img_sql, img_cut)
                    self.recognitions.append((i, bool_flag, distance))

                print('11111')
                for i in range(images_num):
                    recog_res = ':  Same Person' if self.recognitions[i][1] else ':  Different Person'
                    self.mylist.insert(tk.END, 'Person' + str(
                        self.recognitions[i][0]) + recog_res + '    Distance:' + str(
                        self.recognitions[i][2]) + '\n', )

    # def __compare__thread__(self, i, img_sql):
    #     print('tread:{}'.format(i))
    #     path_cut = self.path_capture_dir + 'person' + str(i) + '.png'
    #     img_cut = Image.open(path_cut)
    #     bool_flag, distance = self.Net_base(img_sql, img_cut)
    #     lock2.acquire()
    #     self.recognitions.append((i, bool_flag, distance))
    #     print('thrad:2_{}'.format(i))
    #     lock2.release()

    def find(self):
        p = threading.Thread(target=self.__find__)
        p.start()

    def __find__(self):
        images_num = len(os.listdir(self.path_capture_dir))
        if images_num == 0:
            messagebox.showerror(title='Error', message='Please cut first')
        else:
            threadings = []
            self.findings = []
            for i in range(images_num):
                img_cut_path = self.path_capture_dir + 'person' + str(i) + '.png'
                img_cut = Image.open(img_cut_path)
                sql = 'SELECT * FROM Persons'
                cur.execute(sql)
                res = cur.fetchall()
                print(res)
                if len(res) == 0:
                    messagebox.showerror(title='Error', message='there is no datas in SQL!')
                    break
                else:
                    p = self.NetFind(img_cut, sql_res=res, i=i)
                    threadings.append(p)
            print(threadings)
            for item in threadings:
                item.join()
            print(self.findings)
            self.findings.sort(key=lambda i: i[0])
            print(self.findings)
            ###############################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # display
            self.right_imgs.images = []
            labal = tk.Label(self.right_imgs).place(relx=0, rely=0.85, relwidth=1, relheight=0.15)
            for i in range(images_num):
                if self.findings[i][1] == True:
                    img_sql_path = self.findings[i][-1]
                    img = Image.open(img_sql_path)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.right_imgs.create_image((0 + i * 180, 0), anchor=tk.NW, image=imgtk)
                    self.right_imgs.images.append(imgtk)
                    labal = tk.Label(self.right_imgs,
                                     text='person{}\n{}\ndis={}\n'.format(self.findings[i][0], self.findings[i][2],
                                                                          self.findings[i][3]))
                    labal.place(x=0 + i * 180, y=200, w=180)
                else:
                    labal = tk.Label(self.right_imgs,
                                     text='person{}\n{}\n'.format(self.findings[i][0], 'Not in SQL'))
                    labal.place(x=0 + i * 180, y=200, w=180)

    def NetFind(self, img_cut, sql_res, i):
        p = threading.Thread(target=self.__NetFind__, args=(img_cut, sql_res, i,))
        p.start()
        return p

    def __NetFind__(self, img_cut, sql_res, i):
        ##################################################################！！！！！
        distance_min = -1
        bool_flag_init = False
        name_res = None
        pic_path_res = None
        res = (i, False, None, -1, None)
        for item in sql_res:
            name, pic_path = item[1], item[2]
            img_sql = Image.open(pic_path)
            bool_flag, distance = self.Net_base(img_sql, img_cut)
            if bool_flag == True:
                distance_min = distance
                bool_flag_init = bool_flag
                name_res = name
                pic_path_res = pic_path
                break
        if bool_flag_init == True:
            res = (i, True, name_res, distance_min, pic_path_res)
        print('thread:', res)
        lock3.acquire()
        self.findings.append(res)
        lock3.release()

    def Net_base(self, img_sql, img_cut):
        '''
        :param a: image1
        :param b: image2
        :return: destance, if same person
        (distance, True)
        '''
        res, dis = compare.compare(img_sql, img_cut)
        return res, dis


class detector_mtcnn:
    def __init__(self):
        self.path = './datas/downloads/'
        pass

    def capture(self):
        image = Image.open(self.path + 'download.png')
        bounding_boxes, landmarks = mymtcnnlib.detector.detect_faces(image)
        torch.save(bounding_boxes, self.path + 'boxes')
        global person_num
        person_num = bounding_boxes.shape[0]
        image = mymtcnnlib.utils.show_bboxes(image, bounding_boxes, landmarks, width=0)
        del_file(self.path + 'persons')
        threadings = []
        for i in range(person_num):
            p = threading.Thread(target=self.getpic_for_all, args=(image, bounding_boxes[i, :-1], i,))
            p.start()
            threadings.append(p)
        for item in threadings:
            item.join()

    def getpic_for_all(self, image, bounding_box, index):
        res = image.crop(bounding_box)
        # 增加缩放########### here
        height = 200
        w, h = res.size
        # print(w, h)
        res = res.resize((w * height // h, height))
        res.save(self.path + 'persons/person' + str(index) + '.png')


################################
def del_file(path):
    '''
    :param path: 目录
    :return: 删除目录下的所有文件
    '''
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)


def selectPath():
    # 选择文件path_接收文件地址
    path = filedialog.askopenfilename()
    # print(path)
    return path


if __name__ == '__main__':
    del_file('./datas/downloads/persons/')
    cap = cv2.VideoCapture(0)
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    print(w, h)
    root.geometry(str(w) + 'x' + str(h))
    # root.resizable(width=False, height=False)
    root.title("Face Recognition")
    c = Frame_left_up(root)
    d = Frame_right_up(root)
    e = Frame_down(root)
    # c.__showimage__()
    # c.show_video()
    # c.__show_video_right__()
    # c.thread()
    root.mainloop()
