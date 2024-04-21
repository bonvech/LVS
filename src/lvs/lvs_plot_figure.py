import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib import dates
import os
from datetime import datetime


days_to_plot = 14


############################################################################
##  Return possible datatime format
############################################################################
def get_time_format():
    ##  check if format is possible
    fmt = dates.DateFormatter('%d-%2m-%Y\n %H:%M')
    try:
        print(datetime.now().strftime(fmt))
    except:
        fmt = dates.DateFormatter('%d/%m/%Y\n %H:%M')
    return fmt


############################################################################
##  Get folder separator sign
############################################################################
def get_folder_separator():

    if 'ix' in os.name:
        sep = '/'  ## -- path separator for LINIX
    else:
        sep = '\\' ## -- path separator for Windows
    return sep


############################################################################
##  Prepare data to plot graphs
############################################################################
def get_year_from_filename(name):
    if 'ix' in os.name:
        sep = '/'  ## -- path separator for LINIX
    else:
        sep = '\\' ## -- path separator for Windows

    year  = name.split(sep)[-1].split('_')[0]
    month = name.split(sep)[-1].split('_')[1]
    return int(year), int(month)


############################################################################
##  Get data from previous_month
############################################################################
def get_data_from_previous_month(name):
    sep = get_folder_separator()

    ##  get actual year and month
    year, month = get_year_from_filename(name)

    ##  calculate previous year and month
    newmonth =   12    if month == 1 else month - 1 
    newyear = year - 1 if month == 1 else year
    if debug_mode:
        print(newyear, newmonth)

    ##  replace year and month in filename
    if debug_mode:
        print(name)
    nparts = name.split(sep)
    nfile = nparts[-1].split('_')
    nfile[0] = str(newyear)
    nfile[1] = f'{newmonth:02d}'
    nparts[-1] = '_'.join(nfile)
    newname = sep.join(nparts)
    if debug_mode:
        print(f"newname = {newname}")

    ## check data file
    if not os.path.exists(newname):
        if debug_mode:
            print(newname, "is not found")
        return -1
    else:
        if debug_mode:
            print(newname, "exists")

    ## get previous month data
    data = read_datafile(newname)

    return data


############################################################################
##  Read data file 
############################################################################
def read_datafile(datafilename):
    data = pd.read_csv(datafilename, sep=';')
    data.columns = ['Datetime'] + data.columns[2:].values.tolist() + ['last']
    data['Actual(m3)'] = data['Actual(m3)'].str.replace(',', ".").astype(float)
    #print(data.columns)
    return data
    

############################################################################
##  Prepare data to plot graphs
##  get 2 week data from data files
############################################################################
def prepare_data(datafilename, xcolumn='', ycolumn='Actual(m3)'):
    ## read data from file
    data = read_datafile(datafilename)
    #print(data.head())
    #print(pd.to_datetime(data['Datetime']))

    ##  make column to plot on x axis
    fmt = '%d.%m.%Y %H:%M:%S'
    x = pd.to_datetime(data['Datetime'], format=fmt)
    #print(x)

    ## если данных меньше, чем 2 недели, считать данные за прошлый месяц
    if x.min() + pd.to_timedelta("336:00:00") <= x.max():
        print("One file is enouth")
    else:
        print("Data file has less than 2 week data")
        olddata = get_data_from_previous_month(datafilename)
        print(datafilename, olddata)
        if olddata != -1:
            data = pd.concat([olddata, data], ignore_index=True)
        #print(f"joined data: {data.shape}\n", data.head())
        ## make column to plot on x axis
        x = pd.to_datetime(data['Datetime'], format=fmt)

    data['plotx'] = x

    ##  оставить только две недели
    xmin = x.max() - pd.to_timedelta("336:00:00") ## 14 days
    #print("xmin: ", xmin)
    data = data[pd.to_datetime(data['plotx']) > xmin]
    #print(f"only 2 weeks: {data.shape}\n", data.head())

    return data


############################################################################
## Create plots from data file with LVS/PNS data
#  @param nfigs - number of files to create
############################################################################
def plot_figure_from_data(datum, path_to_figures, name='figure', title="LVS"):
    if debug_mode:
        print(f"Plot  {nfigs}  figures")

    #print(path_to_figures)
    if not os.path.isdir(path_to_figures):
        os.makedirs(path_to_figures)

    ## format graph
    fmt = get_time_format()
    locator = dates.AutoDateLocator(minticks=20, maxticks=30)
    labelrotation=0

    facecolor = 'white'
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['lines.linewidth'] = 3

    ## get 5 days data
    xmin = datum.plotx.max() - pd.to_timedelta(f"{24*days_to_plot}:01:00")  ##  7 days
    #print("xmin: ", xmin)
    data = datum[datum.plotx >= xmin]
    data = create_one_hour_grid(data)
    x = data['plotx']
    y = data['Actual(m3)']

    xlims = (x.min(), x.max() + pd.to_timedelta("2:00:00"))

    if debug_mode:
        print('=============================')
        print(y.values)

    ##########################
    ## Plot figure
    fig = plt.figure(figsize=(10, 5))

    ax_1 = fig.add_subplot(1, 1, 1)
    color = 'purple' if 'lvs' in name.lower() else 'royalblue'
    ax_1.plot(x, y, color=color, label=title)
    ax_1.fill_between(x, y, np.zeros_like(y), color=color)

    ax_1.set_xlim(xlims)
    ax_1.set_ylim(bottom=0)
    ax_1.set_ylabel('Actual (m3)')
    #ax_1.legend()
    ax_1.set_title(title, loc='right')
    
    # Повернем метки рисок на 55 градусов
    ax_1.tick_params(axis='x', labelrotation=labelrotation)
    
    ax_1.xaxis.set_major_formatter(fmt)
    ax_1.xaxis.set_minor_locator(locator)
    ax_1.grid(which='major', alpha=0.9)
    ax_1.grid(which='minor', alpha=0.5, linestyle='--')

    ## save to files
    plotname = path_to_figures + name + '_week'
    fig.savefig(plotname + '.svg', facecolor=facecolor, bbox_inches='tight')
    fig.savefig(plotname + '.png', facecolor=facecolor, bbox_inches='tight') 


############################################################################
## Create plots from data file with LVS/PNS data
#  @param nfigs - number of files to create
############################################################################
def create_one_hour_grid(datum):
    hours = 24 * days_to_plot + 4
    index = pd.date_range(datetime.now() - pd.to_timedelta(f"{hours - 2}:01:00"), periods=hours, freq="h")
    data = pd.DataFrame({"plotx": index}, index=index)
    data['timetomerge'] = index
    data['timetomerge'] = data.apply(lambda x: str(x['timetomerge'])[:13], axis=1)

    datum = datum[['Datetime', 'Actual(m3)','plotx']]
    datum.loc[:, ['timetomerge']] = datum.apply(lambda x: str(pd.to_datetime(x['Datetime'], 
                                                 format='%d.%m.%Y %H:%M:%S'))[:13], axis=1)
    datum = datum.drop_duplicates(subset='timetomerge', keep='first')

    ## merge datatframes
    data = pd.merge(data, datum[['Actual(m3)', 'timetomerge']],  on='timetomerge', how='left')
    data = data.fillna(0)

    #print(data)  
    return data


## --------------------------------------------------------------------------------------------------
## --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    ##  read device name from configfile
    try:
        import lvs_config as config
        device_name = config.device_name
    except:
        device_name = 'LVS'
        
    debug_mode = False
    sep = get_folder_separator()
    dirname = "." + sep + "data" + sep
    path_to_figures = "." + sep + "figures" + sep
    
    ## get current data file name
    timestamp = str(datetime.now())[:7].replace('-', '_')    #'2022_11'  #'2022_06'
    if debug_mode:
        print("timestamp:", timestamp)
    filename = timestamp + f'_{device_name.split()[0].lower()}_data.csv'
    datafilename = dirname + filename

    ## check data file
    if not os.path.exists(datafilename):
        #if debug_mode:
            print(datafilename, "is not found")
    else:
        if debug_mode:
            print(datafilename, "exists")

    ## check path to figures
    #print(path_to_figures)
    if not os.path.isdir(path_to_figures):
        os.makedirs(path_to_figures)

    ## read and prepare data
    datum = prepare_data(datafilename)
    if debug_mode:
        print(datum.head(2))

    # create figure
    plot_figure_from_data(datum, 
                          path_to_figures, 
                          name=device_name.split()[0].lower(), 
                          title=device_name)
