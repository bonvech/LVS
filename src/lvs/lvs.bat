echo LVS Start
echo "lvs.bat Start" >> lvs.log
d:
cd D:\AA\LVS\src\
start /min python main.py
start /min python lvs_plot_figure.py
echo "lvs.bat End" >> lvs.log

