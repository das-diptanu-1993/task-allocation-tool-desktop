import plotly.express as px
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
import webbrowser
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# data = [ {"Task":"t1", "Start":"2021-01-10", "Finish":"2021-01-20", "Resource":"r1"} ]
def get_figure_using_express(data):
    df = pd.DataFrame(data)
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
    fig.update_yaxes(autorange="reversed")
    return fig

def native_plot_gantt(data):
    fig = ff.create_gantt(data)
    return fig

def plot_figure_remotely(fig):
    fig.show()
    return

def plot_figure_natively(fig):
    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(figure=fig)])
    webbrowser.open("http://127.0.0.1:8050/")
    print("Press CTRL+C to Restart Program")
    app.run_server(debug=True, use_reloader=False)
    return

def modify_data_format(data):
    modified_data = {'Task': {}, 'Resource': {}, 'Start': {}, 'End':{}, 'Completion': {}}
    for i in range(len(data)):
        modified_data['Task'][i] = data[i]['Task']
        modified_data['Resource'][i] = data[i]['Resource']
        modified_data['Start'][i] = pd.Timestamp(data[i]['Start'])
        modified_data['End'][i] = pd.Timestamp(data[i]['Finish'])
        modified_data['Completion'][i] = 0.0
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

def plot_figure_standalone(data, c_dict=c_dict):
    data = modify_data_format(data)
    df = pd.DataFrame(data)
    proj_start = df.Start.min()
    df['start_num'] = (df.Start-proj_start).dt.days
    df['end_num'] = (df.End-proj_start).dt.days
    df['days_start_to_end'] = df.end_num - df.start_num
    df['current_num'] = (df.days_start_to_end * df.Completion)
    df['color'] = df.apply(color, axis=1)
    # Creating Plot ...
    fig, (ax, ax1) = plt.subplots(2, figsize=(16,6),
                                  gridspec_kw={'height_ratios':[6, 1]},
                                  facecolor='#36454F')
    ax.set_facecolor('#36454F')
    ax1.set_facecolor('#36454F')
    ax.barh(df.Task, df.current_num, left=df.start_num, color=df.color)
    ax.barh(df.Task, df.days_start_to_end, left=df.start_num, color=df.color, alpha=0.5)
    for idx, row in df.iterrows():
        ax.text(row.end_num+0.1, idx, f"{int(row.Completion*100)}%", va='center', alpha=0.8, color='w')
        ax.text(row.start_num-0.1, idx, row.Task, va='center', ha='right', alpha=0.8, color='w')
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
    plt.suptitle('PROJECT XYZ', color='w')
    legend_elements = []
    for key, value in c_dict.items():
        legend_elements.append(Patch(facecolor=value, label=key))
    legend = ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)
    plt.setp(legend.get_texts(), color='w')
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_xticks([])
    ax1.set_yticks([])
    plt.show()
    plt.savefig('gantt.png', facecolor='#36454F')
    
