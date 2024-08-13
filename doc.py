
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use("paper")
from py2ls import netfinder as nt
import webbrowser
from py2ls.ips import *

# Configure Jupyter notebook
try:
    get_ipython().run_line_magic('load_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
except NameError:
    pass 

def download_mpl(url, keyword,fmt=f'https://matplotlib.org/stable/api/_as_gen/matplotlib.'):
    url_plt = url #"https://matplotlib.org/stable/api/pyplot_summary.html"
    # txt=nt.fetch(url_plt, where='div',what="bd-toc-item navbar-nav")
    txt=nt.fetch(url_plt, where='li',what="toctree-l1 current active has-children")

    keys_=txt[0].split(f'matplotlib.{keyword}')[2:]
    keys_corr=[]
    [keys_corr.append('matplotlib.'+keyword+i) for i in keys_]
    # example: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.cla.html
    url_base = f'{fmt}{keyword}'
    url_tail = '.html'
    url_pool_plt=[]
    [url_pool_plt.append(url_base+funcname+url_tail) for funcname in keys_]

    dict_plt=dict(zip(keys_corr,url_pool_plt))
    return dict_plt

def download_sns():
    # get the function list
    url_sns = "https://seaborn.pydata.org/api.html#"
    txt=nt.fetch(url_sns, where='div',what="bd-toc-item navbar-nav")

    keys_=ssplit(txt,by='seaborn')[1:]
    keys_corr=[]
    [keys_corr.append('sns'+i) for i in keys_]

    # example: https://seaborn.pydata.org/generated/seaborn.objects.Plot.pair.html
    url_base = 'https://seaborn.pydata.org/generated/seaborn'
    url_tail = '.html'
    url_pool_sns=[]
    [url_pool_sns.append(url_base+funcname+url_tail) for funcname in keys_]

    dict_sns=dict(zip(keys_corr,url_pool_sns))

    # save to a file as a json
    dir_curr_script=get_cwd()
    dir_dict_sns=dir_curr_script+"/data/docs_links.json"
    fsave(dir_dict_sns, dict_sns)
    return dict_sns
def doc(keyword:str=None):
    dir_curr_script=get_cwd()
    dir_dict_sns=dir_curr_script+"/data/docs_links.json"
    try: 
        with open(dir_dict_sns, 'r') as file:
            dict_sns = json.load(file)
    except:
        dict_sns= download_sns()
    fit_str,fit_idx = strcmp(keyword, list(dict_sns.keys()),verbose=0)
    webbrowser.open(dict_sns[fit_str])
    return dict_sns[fit_str]


def doc_add(dict_):
    dir_curr_script=get_cwd()
    dir_dict_sns=dir_curr_script+"/data/docs_links.json"
    with open(dir_dict_sns, 'r') as file:
            dict_sns = json.load(file)
    dict_sns.update(dict_) 
    fsave(dir_dict_sns, dict_sns)

def doc_new():
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.Animation.html",
                            keyword="animation"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html",
                            keyword="figure"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/projections/polar.html",
                            keyword="projections"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.ArrowStyle.html",
                            keyword="patches"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.markers.MarkerStyle.html",
                            keyword="markers"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html",
                            keyword="lines"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.artist.Artist.add_callback.html",
                            keyword="artist"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.AsinhNorm.html",
                            keyword="colors"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/axes_api.html",
                            keyword="axes"))
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/axis_api.html",
                            keyword="axis") )
    doc_add(download_mpl(url="https://matplotlib.org/stable/api/pyplot_summary.html",
                            keyword="pyplot")) 

def main():
    doc('pyplot legend')

if __name__=='__main__':
    main()