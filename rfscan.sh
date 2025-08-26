cd /home/sine/opt/rfscan
python3 rfscan.py
cat scan-* > /home/sine/Documents/Shure/"Frequency Plots"/$(date +"%Y-%m-%d_%I-%M-%S%p").csv
rm scan-*
