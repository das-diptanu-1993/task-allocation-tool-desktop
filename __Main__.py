from __Utility__ import *

def __Main__(t_r_map=None, d_p_map=None, process_start=None):
    ''' Debuug '''
    # Welcome Script ...
    print("----------------")
    print("----------------")
    print("RESOURCE PLANNER")
    print("----------------")
    print("----------------")
    if(t_r_map==None):
        # Collecting T_R_MAP ...
        t_r_map_collected = False
        while(t_r_map_collected == False):
            T_R_MAP = input("\n\nEnter CSV File Path for `Resource Task Completion Data`:")
            t_r_map = get_map_from_csv(T_R_MAP)
            if t_r_map == None:
                print("Invalid File: {}".format(T_R_MAP))
                continue
            if not(validate_task_resource_map(t_r_map)):
                print("Unable to validate [Task, Resource] Mapping.")
                continue
            t_r_map_collected = True
    if(d_p_map==None):
        # Collecting D_P_MAP ...
        d_p_map_collected = False
        while(d_p_map_collected == False):
            D_P_MAP = input("\n\nEnter CSV File Path for `Task Dependency Data`:")
            d_p_map = get_map_from_csv(D_P_MAP)
            if d_p_map == None:
                print("Invalid File: {}".format(D_P_MAP))
                continue
            if not(validate_dependency_map(d_p_map)):
                print("Unable to validate D_P_MAP.")
                continue
            d_p_map_collected = True
    if(process_start==None):
        # Collecting Process Start-Date ...
        start_date_collected = False
        while(start_date_collected == False):
            try: 
                date_entry = input("\n\nEnter Process Start Date [YYYY-MM-DD]:")
                year, month, day = map(int, date_entry.split('-'))
                process_start = date(year, month, day)
            except Exception as error:
                print("Error: {}".format(error))
                continue
            start_date_collected = True
    # Processing Data ...
    t0 = get_time()
    #t_list = get_task_list(t_r_map)
    t_list = get_sorted_task_list(d_p_map)
    r_group = get_resource_group(t_list, t_r_map)
    r_alloc_list = get_allocation_list(r_group)
    alloc_timeline_dict_list = []
    process_end_list = []
    min_end, optimized_timeline, recommended_alloc = None, None, None
    for alloc in r_alloc_list:
        t_timeline_dict = {}
        for task in t_list:
            get_start_end(task, t_list, alloc,
                          d_p_map, t_r_map, t_timeline_dict, process_start)
        alloc_timeline_dict_list.append(t_timeline_dict)
        process_end = get_process_timeline_end(t_timeline_dict)
        process_end_list.append(process_end)
        if min_end == None:
            min_end = process_end
            optimized_timeline = t_timeline_dict
            recommended_alloc = alloc
        elif min_end > process_end:
            min_end = process_end
            optimized_timeline = t_timeline_dict
            recommended_alloc = alloc
    t1 = get_time()
    # Printing Resource Allocation Recommendations ...
    print('\n\n-----------------------')
    print('Recommended Allocation:')
    print('-----------------------')
    print('Task → Resource')
    print('---------------')
    recommendation = []
    for i in range(len(t_list)):
        print("{} → {}".format(t_list[i], recommended_alloc[i]))
        recommendation.append([t_list[i], recommended_alloc[i]])
    # Printing Task Start & End Timeline
    print('\n\nTask → Start_Date → End_Date')
    print('------------------------------')
    task_timeline_list = []
    for task, timeline in optimized_timeline.items():
        print("{} → {} → {}".format(task, timeline[0], timeline[1]))
        task_timeline_list.append([task, timeline[0], timeline[1]])
    # Printing Process Data
    print('\n\nProcess Start-Date: %s\nProcess End-Date: %s\nCode Execution Time: %.2f'
           % (process_start, min_end, (t1-t0)))
    print('------------------------------------\n\n')
    
    plot_data = []
    for i in range(len(t_list)):
        plot_data.append(dict(Task = t_list[i],
                              Start = optimized_timeline[t_list[i]][0],
                              Finish = optimized_timeline[t_list[i]][1],
                              Buffer = optimized_timeline[t_list[i]][3],
                              Resource = recommended_alloc[i] ))
    plot_table("INPUT: RESOURCE TASK COMPLETION DATA",
               t_r_map, ['Task', 'Resource', 'Duration', 'Buffer'])
    plot_table("INPUT: TASK DEPENDENCY DATA",
               d_p_map, ['Dependent Task', 'Precedent Task'])
    plot_table("OUTPUT: RESOURCE ALLOCATION RECOMMENDATION",
               recommendation, ['Task', 'Resource'])
    plot_table("OUTPUT: OPTIMIZED TASK TIMELINES",
               task_timeline_list, ['Task', 'Start', 'End'])
    plot_figure_standalone(plot_data)
    show_plots()
    return True

def get_process_timeline_end(t_timeline_dict):
    end = None
    for task, timeline in t_timeline_dict.items():
        if end == None:
            end = timeline[1]
        elif end < timeline[1]:
            end = timeline[1]
    return end

''' t_timeline is a dictionary storing start, end of task '''
def get_start_end(task, t_list, r_alloc, d_p_map, t_r_map,
                  t_timeline_dict = {}, process_start = date.today()):
    if task in t_timeline_dict.keys():
        #print("Optimized Process.")
        return t_timeline_dict[task]
    resource, p_t_list = get_dependency(task, t_list, r_alloc, d_p_map)
    duration = 0
    buffer_ratio = 0
    for t_r in t_r_map:
        if (t_r[0] == task) and (t_r[1] == resource):
            duration = t_r[2]
            try:
                duration += t_r[3]
                buffer_ratio = float(t_r[3]) / float(duration)
            except IndexError:
                pass
            break
    start = process_start
    if len(p_t_list) == 0:
        start = process_start
    elif (len(p_t_list) == 1) and (p_t_list[0] == None):
        start = process_start
    else:
        for p_t in p_t_list:
            if p_t == None:
                continue
            p_t_start, p_t_end, p_t_duration, p_t_buffer_ratio = get_start_end(
                p_t, t_list, r_alloc, d_p_map, t_r_map, t_timeline_dict, process_start)
            if p_t_end > start:
                start = work_day_add(p_t_end, 1)
    end = work_day_add(start, duration)
    '''
    print("Task: {} | Start: {} | End: {} | Duration: {}"
          .format(task, start, end, duration))
          '''
    t_timeline_dict[task] = [start, end, duration, buffer_ratio]
    return [start, end, duration, buffer_ratio]

def get_dependency(task, t_list, r_alloc, d_p_map):
    p_list = []
    for d_p in d_p_map:
        if d_p[0] == task:
            p_list.append(d_p[1])
    #print("Task: {} | Precedent Tasks: {}".format(task, p_list))
    try:
        t_index = t_list.index(task)
    except ValueError:
        return None
    resource = r_alloc[t_index]
    r_t_list = []
    for i in range(t_index):
        if r_alloc[i] == resource:
            r_t_list.append(t_list[i])
    #print("Task: {} | Resource Tasks: {}".format(task, r_t_list))
    return [resource, [*p_list, *r_t_list]]

def get_sorted_task_list(d_p_map):
    t_order_list = {}
    for d_p in d_p_map:
        get_task_order(d_p[0], d_p_map, t_order_list)
    t_sorted_list = []
    index = 0
    for order in sorted(t_order_list.values()):
        index += 1
        if index > len(t_sorted_list):
            for t, o in t_order_list.items():
                if o == order:
                    t_sorted_list.append(t)
    return t_sorted_list

def get_task_order(task, d_p_map, t_order_list = {}):
    if task in t_order_list.keys():
        return t_order_list[task]
    t_order = 0
    for d_p in d_p_map:
        if d_p[0] == task:
            if d_p[1] == None and t_order == 0:
                continue
            if d_p[1].strip() == "" and t_order == 0:
                continue
            p_t_order = get_task_order(d_p[1], d_p_map, t_order_list)
            if p_t_order >= t_order:
                t_order = p_t_order + 1
    t_order_list[task] = t_order
    return t_order    

def get_allocation_list(t_r_group):
    if( len(t_r_group) == 2 ):
        return [ [i, j] for i in t_r_group[0] for j in t_r_group[1] ]
    else:
        r_group = t_r_group.pop()
        return [ [*i, j] for i in get_allocation_list(t_r_group) for j in r_group ]

def get_resource_group(t_list, t_r_map):
    t_r_group = []
    for t in t_list:
        r_group = []
        for t_r in t_r_map:
            if(t_r[0] == t):
                r_group.append(t_r[1])
        t_r_group.append(r_group)
    return t_r_group

def get_task_list(t_r_map):
    t_list = []
    for t_r in t_r_map:
        try:
            t_list.index(t_r[0])
        except ValueError:
            t_list.append(t_r[0])
        except:
            pass
    return t_list

def get_resource_list(t_r_map):
    r_list = []
    for t_r in t_r_map:
        try:
            r_list.index(t_r[1])
        except ValueError:
            r_list.append(t_r[1])
        except:
            pass
    return r_list

def validate_task_resource_map(t_r_map):
    row = 0
    for t_r in t_r_map:
        row += 1
        if len(t_r) < 3:
            print("Missing data at ROW: %d" % (row) )
            return False
        try:
            if not(t_r[2].isnumeric()):
                print("Wrong work-day param at ROW: %d" % (row) )
                return False
        except AttributeError:
            if not(isinstance(t_r[2], int)):
                print("Wrong work-day param at ROW: %d" % (row) )
                return False
    return True

def validate_dependency_map(d_p_map):
    row_count = 0
    for d_p in d_p_map:
        row_count += 1
        if(len(d_p) < 2):
            print("Missing data at ROW: %d" % (row_count) )
            return False
    return True

# Executing Main ...
if __name__ == '__main__':
    __Main__()

