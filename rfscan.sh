mkdir .scandata
cd .scandata
python3 ../rfscan.py
cat scan-* > /home/sine/Documents/Shure/"Frequency Plots"/$(date +"%Y-%m-%d_%I-%M-%S%p").csv
cd ..
rm -r ./.scandata
