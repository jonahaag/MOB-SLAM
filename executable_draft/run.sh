#!/bin/bash             

# first add matlab to path variable, e.g. via export PATH="$PATH:/Applications/MATLAB_R2020b.app/bin/"
# alternative options such as -nodisplay -nosplash available                                                                                
matlab -r "matlab.engine.shareEngine" & sleep 5m && python3 main.py
# pyinstaller src/main.py -n ModelBasedSLAM --noconsole -i icon_draft.icns --onefile