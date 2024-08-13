import os
from datetime import datetime
import subprocess
import re

def export_requirements(fpath="/Users/macjianfeng/Dropbox/github/python/py2ls/", exclude=["py2ls","jaraco"]):
    """
    Main function to generate a timestamped requirements file and convert it to Poetry dependencies.
    """
    if not fpath.endswith('/'):
        fpath+='/'
    with open(os.path.join(fpath,'pyproject.toml'),'r') as f:
        txt=f.read()
    txt_list = re.split('\n',txt)

    idx_start=[i for i,item in enumerate(txt_list) if item.startswith('[tool.poetry.dependencies]')][0]+2
    idx_stop=[i for i,item in enumerate(txt_list) if item.startswith('[build-system]')][0]

    # keep the head info
    txt_list_head=txt_list[:idx_start]
    txt_list_tail=txt_list[idx_stop:]

    # keep the tail info
    txt_list_head=[i+"\n" for i in txt_list_head]
    txt_list_tail=[i+"\n" for i in txt_list_tail]

    # filename
    current_time = datetime.now().strftime("%Y-%m-%d")
    fpath_requirements = f"{fpath}requirements_{current_time}.txt"

    os.makedirs(os.path.dirname(fpath_requirements), exist_ok=True)

    # get the updated requirements.txt
    try:
        with open(fpath_requirements, 'w') as requirements_file:
            subprocess.run(['pip', 'freeze'], stdout=requirements_file, check=True)
        print(f"Requirements have been saved to {fpath_requirements}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while creating the requirements file: {e}")
        
    # open the orgi toml file
    try:
        with open(fpath_requirements, 'r') as file:
            txt = file.read()
    except Exception as e:
        print(f"An error occurred while reading the requirements file: {e}")

    # convert to poetry
    txt_corr=[]
    for txt_ in re.split('\n', txt):
        if len(txt_) <=40 and not txt_=='':
            txt_corr.append(txt_.replace("==",' = ">=')+'"\n')

    # add a newline
    txt_corr.append('\n')

    # merge 
    txt_corr_=[*txt_list_head, *txt_corr, *txt_list_tail]

    # rm .txt
    # os.remove(fpath_requirements)

    # fsave
    with open(f"{fpath}pyproject_{current_time}.toml", 'w') as f:
        f.writelines(txt_corr_)

def main():
    export_requirements(fpath="/Users/macjianfeng/Dropbox/github/python/py2ls/")

if __name__ == "__main__":
    main()
