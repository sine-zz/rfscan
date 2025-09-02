WD=$(pwd)
mkdir /tmp/rfscan
cd /tmp/rfscan
python3 $WD/rfscan.py
cat /tmp/rfscan/scan-* > ~/Documents/Shure/"Frequency Plots"/$(date +"%Y-%m-%d_%I-%M-%S%p").csv
cd
rm -r /tmp/rfscan
