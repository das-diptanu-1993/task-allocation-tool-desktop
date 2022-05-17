from datetime import date, timedelta
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import time
import sys

def get_time():
    return time.time()

def clear_all():
    sys.modules[__name__].__dict__.clear()
    return

def show_plots(plt=plt):
    plt.show()

def plot_table(table_name, data, header):
    fig, ax = plt.subplots(figsize=(16,9))
    fig.canvas.manager.set_window_title(table_name)
    # hide axes
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')
    df = pd.DataFrame(data, columns=header)
    ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='left')
    fig.tight_layout()
    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.state('zoomed')
    plt.suptitle(table_name)

# data = [ {"Task":"t1", "Start":"2021-01-10", "Finish":"2021-01-20", "Resource":"r1", "Buffer":0.1 } ]
def modify_data_format(data):
    modified_data = {'Task': {}, 'Resource': {}, 'Start': {}, 'End':{}, 'Buffer': {}}
    for i in range(len(data)):
        modified_data['Task'][i] = data[i]['Task']
        modified_data['Resource'][i] = data[i]['Resource']
        modified_data['Start'][i] = pd.Timestamp(data[i]['Start'])
        modified_data['End'][i] = pd.Timestamp(data[i]['Finish'])
        modified_data['Buffer'][i] = data[i]['Buffer']
    return modified_data

# Function to create random color ...
def random_color():
    r = lambda: random.randint(0,127)
    return ('#%02X%02X%02X' % (128+r(),128+r(),128+r()))

# Creating color dictionary ...
c_dict = {}

# create a column with the color for each Resource
def color(row):
    if row['Resource'] in c_dict:
        return c_dict[row['Resource']]
    else:
        c_dict[row['Resource']] = random_color()
        return c_dict[row['Resource']]

def empty_c_dict():
    c_dict = {}

def plot_figure_standalone(data):
    data = modify_data_format(data)
    df = pd.DataFrame(data)
    proj_start = df.Start.min()
    df['start_num'] = (df.Start-proj_start).dt.days
    df['end_num'] = (df.End-proj_start).dt.days
    df['days_start_to_end'] = df.end_num - df.start_num
    df['current_num'] = (df.days_start_to_end * (1-df.Buffer))
    df['color'] = df.apply(color, axis=1)
    # Creating Plot ...
    fig, (ax, ax1) = plt.subplots(2, figsize=(16,9),
                                  gridspec_kw={'height_ratios':[6, 1]},
                                  facecolor='#36454F')
    fig.canvas.manager.set_window_title('OUTPUT: PROJECT GANTT')
    ax.set_facecolor('#36454F')
    ax1.set_facecolor('#36454F')
    ax.barh(df.Task, df.current_num, left=df.start_num, color=df.color)
    ax.barh(df.Task, df.days_start_to_end, left=df.start_num, color=df.color, alpha=0.5)
    for idx, row in df.iterrows():
        ax.text(row.end_num+0.1, idx, f"Buffer = {int(row.Buffer*100)}%",
                va='center', alpha=0.8, color='w')
        ax.text(row.start_num-0.1, idx, row.Task, va='center', ha='right',
                alpha=0.8, color='w')
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='k', linestyle='dashed', alpha=0.4, which='both')
    xticks = np.arange(0, df.end_num.max()+1, 3)
    xticks_labels = pd.date_range(proj_start, end=df.End.max()).strftime("%m/%d")
    xticks_minor = np.arange(0, df.end_num.max()+1, 1)
    ax.set_xticks(xticks)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticklabels(xticks_labels[::3], color='w')
    ax.set_yticks([])
    plt.setp([ax.get_xticklines()], color='w')
    ax.set_xlim(0, df.end_num.max())
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('w')
    plt.suptitle('PROJECT GANTT', color='w')
    legend_elements = []
    for key, value in c_dict.items():
        if key in data['Resource'].values():
            legend_elements.append(Patch(facecolor=value, label=key))
    legend = ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)
    empty_c_dict()
    plt.setp(legend.get_texts(), color='w')
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_xticks([])
    ax1.set_yticks([])
    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.state('zoomed')
    return True

# Define the weekday mnemonics to match the date.weekday function
(MON, TUE, WED, THU, FRI, SAT, SUN) = range(7)

def work_day_delta(start_date, end_date, work_days = (MON,TUE,WED,THU,FRI)):
    delta_days = (end_date - start_date).days + 1
    full_weeks, extra_days = divmod(delta_days, 7)
    num_workdays = (full_weeks + 1) * len(work_days)
    for d in range(1, 8 - extra_days):
                if (end_date + timedelta(d)).weekday() in work_days:
                                num_workdays -= 1
    return num_workdays

def work_day_add(start_date, duration, work_days = (MON,TUE,WED,THU,FRI)):
    weeks, days = divmod(duration, len(work_days))
    new_date = start_date + timedelta(weeks=weeks)
    for i in range(days):
        new_date += timedelta(days=1)
        while new_date.weekday() not in work_days:
            new_date += timedelta(days=1)
    return new_date

def get_map_from_csv(file_name):
    try:
        f = open(file_name)
    except FileNotFoundError:
        print("Invalid File Address: {}".format(file_name))
        return None
    except Exception as e:
        print(e)
        return None
    data = f.read()
    row_list = data.split("\n")
    t_r_list = []
    for row in row_list:
        cell_list = row.split(",")
        t_r = []
        for cell in cell_list:
            if cell.isnumeric():
                cell = int(cell)
            if cell == "":
                cell = None
            t_r.append(cell)
        t_r_list.append(t_r)
    return t_r_list[1:-1]
