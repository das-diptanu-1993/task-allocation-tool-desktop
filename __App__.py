from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfile
from tkcalendar import Calendar
import os
from datetime import date
from __Main__ import __Main__, validate_task_resource_map, validate_dependency_map
from __Utility__ import get_map_from_csv

class __App__(Tk):
    def __init__(self, resolution, font):
        super().__init__()
        self.resolution = resolution
        self.font = font
        self.winfo_toplevel().title("Task Allocation Planner")
        super().geometry("{}x{}".format(
            self.resolution[0], self.resolution[1]))
        self.h1 = Label(
            self, text="Task Allocation Planner",
            font=FONT_BIG, bg='black', fg='white')
        self.h1.pack(padx=5, fill=X, side=TOP)
        self.s1 = Label(self, text="")
        self.s1.pack(pady=20)
        self.f123 = Frame(self)
        self.f123.pack(side=TOP, fill=X)
        self.f12 = Frame(self.f123)
        self.f12.pack(side=LEFT)
        # Input 1 ...
        self.l1 = Label(self.f12,
            text="Enter [Task, Resource, Duration, Buffer] CSV File Path: ",
            font=FONT)
        self.l1.pack(padx=5, anchor=NW)
        self.f1 = Frame(self.f12)
        self.f1.pack(side=TOP, fill=X)
        self.e1 = Entry(self.f1, font=FONT, width=35)
        self.e1.pack(padx=5, side=LEFT, fill=NONE)
        self.b1 = Button(self.f1, text="Browse", font=FONT, command=self.set_e1)
        self.b1.pack(padx=5, side=LEFT)
        self.s1 = Label(self.f12, text="")
        self.s1.pack(pady=20)
        # Input 2 ...
        self.l2 = Label(self.f12,
            text="Enter [Dependent Task, Precedent Task] CSV File Path: ",
            font=FONT)
        self.l2.pack(padx=5, anchor=NW)
        self.f2 = Frame(self.f12)
        self.f2.pack(side=TOP, fill=X)
        self.e2 = Entry(self.f2, font=FONT, width=35)
        self.e2.pack(padx=5, side=LEFT, fill=NONE)
        self.b2 = Button(self.f2, text="Browse", font=FONT, command=self.set_e2)
        self.b2.pack(padx=5, side=LEFT, fill=X)
        self.s2 = Label(self.f12, text="")
        self.s2.pack(pady=20)
        # Input 3 ...
        self.f3 = Frame(self.f123)
        self.f3.pack(side=LEFT, padx=10)
        self.l3 = Label(self.f3,
            text="Enter Process Start Date: ",
            font=FONT)
        self.l3.pack(padx=5, anchor=NW)
        today = date.today()
        self.c3 = Calendar(self.f3, font = FONT, selectmode = 'day', 
            year = today.year, month = today.month, day = today.day)
        self.c3.pack(padx=5, anchor=NW)
        self.s3 = Label(self.f3, text="")
        self.s3.pack(pady=5)
        self.b4 = Button(self, text="OPTIMIZE", font=FONT, 
            command=self.execute_main, bg='grey', fg='black')
        self.b4.pack(padx=5, side=TOP)
    def get_e1(self):
        return self.e1.get()
    def set_e1(self):
        self.e1.delete(0, len(self.get_e1()))
        file = filedialog.askopenfile(mode='r', filetypes=[('CSV', '*.csv')])
        if file:
            filepath = os.path.abspath(file.name)
            print(str(filepath))
            self.e1.insert(0, str(filepath))
            return True
        return False
    def get_e1_csv_data(self):
        t_r_csv_path = self.get_e1()
        t_r_map = get_map_from_csv(t_r_csv_path)
        if t_r_map == None:
            print("Invalid File: {}".format(t_r_csv_path))
            messagebox.showerror("Error", "Invalid File: {}".format(t_r_csv_path))
            return None
        if not(validate_task_resource_map(t_r_map)):
            print("Invalid Mapping: {}".format(t_r_csv_path))
            messagebox.showerror("Error", "Invalid Mapping: {}".format(t_r_csv_path))
            return None
        return t_r_map
    def get_e2(self):
        return self.e2.get()
    def set_e2(self):
        self.e2.delete(0, len(self.get_e2()))
        file = filedialog.askopenfile(mode='r', filetypes=[('CSV', '*.csv')])
        if file:
            filepath = os.path.abspath(file.name)
            print(str(filepath))
            self.e2.insert(0, str(filepath))
            return True
        return False
    def get_e2_csv_data(self):
        d_p_csv_path = self.get_e2()
        d_p_map = get_map_from_csv(d_p_csv_path)
        if d_p_map == None:
            print("Invalid File: {}".format(d_p_csv_path))
            messagebox.showerror("Error", "Invalid File: {}".format(d_p_csv_path))
            return None
        if not(validate_dependency_map(d_p_map)):
            print("Invalid Mapping: {}".format(d_p_csv_path))
            messagebox.showerror("Error", "Invalid Mapping: {}".format(d_p_csv_path))
            return None
        return d_p_map
    def get_c3(self):
        date_entry = self.c3.get_date()
        month, day, year = map(int, date_entry.split('/'))
        return date(2000+year, month, day)
    def execute_main(self):
        t_r_map = self.get_e1_csv_data()
        d_p_map = self.get_e2_csv_data()
        process_start = self.get_c3()
        if t_r_map == None or d_p_map == None or process_start == None:
            print("Invalid Input Entered.")
            messagebox.showerror("Error", "Invalid Input.")
            return False
        __Main__(t_r_map, d_p_map, process_start)

if __name__ == '__main__':
    RESOLUTION = [1366, 768]
    FONT_BIG = ("Arial Rounded MT Bold", 36)
    FONT = ("Arial Rounded MT Bold", 18)
    window = __App__(RESOLUTION, FONT)
    window.mainloop()



