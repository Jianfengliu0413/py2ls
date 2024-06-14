# Install

```python
pip install py2ls
```



# ips

### listdir, basename, dirname, newfolder, finfo

e.g., 

```python
fpath = "....../"
ips.listdir(fpath, kind='pdf', sort_by="size", ascending=0, output = 'df')
```

it filters the ‘.pdf’ files, and sort by the (file-size/name, length of name, create_time, mod_time, last_open_time …) it returns a DataFrame or BoxList (setting by ‘output’)

```python
dir_data, dir_fig = newfolder(fpath, {'data', 'fig'}) # create folder
```

```python
finfo(fpath) # get info: size, creation time, mod time, parent_path, fname, kind...
```

```python
dir_lib(lib_of_interest) # get the fpath
```



### list_func/func_list (same)

list functions in a package

### fload, fsave, figsave

e.g., 

```python
fload(fpath, kind=None, **kwargs)
```

load file (docx, pdf, image, md, json,csv,txt, html, yaml, xml, xlsx…) or save file.

```python
# figsave, as used in matlab. 
figsave(dir_save, "fname.pdf", dpi=300)
```



### pdf2img, img2pdf, docx2pdf

extract images from a PDF, or merge images into a pdf file

```python
pdf2img(dir_pdf, dir_save=None, page=None, kind="png",verbose=True, **kws)
pdf2img(fpath, page=[None, None])  # means extract all pages
# processing page: 1
# processing page: 2
# processing page: 3
# processing page: 4
# processing page: 5

```

```python
img2pdf(dir_img, kind="jpeg",page=None, dir_save=None, page_size="a4", dpi=300)
```

```python
docx2pdf(dir_docx, dir_save) # convert docx to pdf
```

### paper_size

quickly get the size info

```python
paper_size('a4') # [210, 297]
paper_size('card') # [85.6, 53.98]
```



### str2num, num2str, str2list

```python
str2num(“123.345 dollers”,2)# => 123.35 (float) 
```

```python
str2list("abcd") # ['a','b','c','d']
```

```python
list2str(['a','b','c','d']) # 'abcd'
```

### ssplit, sreplace

```python
sreplace(text, dict_replace=None, robust=True)
```

```python
ssplit(text, by="space", verbose=False, **kws) # by = "word", "sentence", ", ","num_strings","digital".....,"length", "upper followed lower", "lower followed upper"
```

```python
text = "The most pronounced physiological changes in sleep occur in the brain.[10] The brain uses significantly less energy during sleep than it does when awake, especially during non-REM sleep. In areas with reduced activity, the brain restores its supply of adenosine triphosphate (ATP), the molecule used for short-term storage and transport of energy.[11] In quiet waking, the brain is responsible for 20% of the body's energy use, thus this reduction has a noticeable effect on overall energy consumption.[12]"
ssplit(text, by=["[10]", "[11]", "[12]"])
# ['The most pronounced physiological changes in sleep occur in the brain.',
# ' The brain uses significantly less energy during sleep than it does when awake, especially during non-REM sleep. In areas with reduced activity, the brain restores its supply of adenosine triphosphate (ATP), the molecule used for short-term storage and transport of energy.',
# " In quiet waking, the brain is responsible for 20% of the body's energy use, thus this reduction has a noticeable effect on overall energy consumption.",
 # '']
```

```python
ssplit(text[:30], by="len", length=5)
# ['The m', 'ost p', 'ronou', 'nced ', 'physi', 'ologi']
```

```python
ssplit(text, by="non_alphanumeric")
# ['The most pronounced physiological changes in sleep occur in the brain.[',
#  '10',
#  '] The brain uses significantly less energy during sleep than it does when awake, especially during non-REM sleep. In areas with reduced activity, the brain restores its supply of adenosine triphosphate (ATP), the molecule used for short-term storage and transport of energy.[',
#  '11',
#  '] In quiet waking, the brain is responsible for ',
#  '20',
#  "% of the body's energy use, thus this reduction has a noticeable effect on overall energy consumption.[",
#  '12',
#  ']']
```

```python
ssplit(text, by="sent")
#['The most pronounced physiological changes in sleep occur in the brain.',
 #'[10] The brain uses significantly less energy during sleep than it does when awake, especially during non-REM sleep.',
 #'In areas with reduced activity, the brain restores its supply of adenosine triphosphate (ATP), the molecule used for short-term storage and transport of energy.',
 #"[11] In quiet waking, the brain is responsible for 20% of the body's energy use, thus this reduction has a noticeable effect on overall energy consumption.",
 #'[12]']
```

```python
ssplit(text, by="lowup")
# ["The most pronounced physiological changes in sleep occur in the brain.[10] The brain uses significantly less energy during sleep than it does when awake, especially during non-REM sleep. In areas with reduced activity, the brain restores its supply of adenosine triphosphate (ATP), the molecule used for short-term storage and transport of energy.[11] In quiet waking, the brain is responsible for 20% of the body's energy use, thus this reduction has a noticeable effect on overall energy consumption.[12]"]

```

```python
sreplace(text, dict_replace=None, robust=True)
```

```python
text= 'The most pronounced physiological changes in sleep occur in the brain.[10] '
 'The brain uses significantly less energy during sleep than it does when '
 'awake, especially during non-REM sleep. In areas with reduced activity, the '
 'brain restores its supply of adenosine triphosphate (ATP), the molecule used '
 'for short-term storage and transport of energy.[11] In quiet waking, the '
 "brain is responsible for 20% of the body's energy use, thus this reduction "
 'has a noticeable effect on overall energy consumption.[12]'
sreplace(text)
"The most pronounced physiological changes in sleep occur in the brain"
sreplace(text,{"sleep":"wakewake"}) # sreplace(text,dict(sleep="wakewake"))
"The most pronounced physiological changes in wakewake occur in the brain."
```

### stats

#### **FuncCmpt** ( two groups cmp)

```python
FuncCmpt(X1, X2, pmc='auto', pair='unpaired')
e.g., 
X1 = [19, 22, 16, 29, 24]
X2 = [20, 11, 17, 12, 22]
p, res = FumcCmpt(X1,X2, pmc='pmc', pair = 'unpair')
# normally distributed
# normally distributed
# unpaired t text
# t(8) = 1.81117, p=0.1077
p,res = FuncCmpt(x1,x2, pmc='pmc',pair='pair')
# paired t test
# t(4)=1.55556,p=0.19479
```

#### FuncMultiCmpt ( multiple groups cmp)

```python
FuncMultiCmpt(pmc='pmc', pair='unpair', data=None, dv=None, factor=None,
                  ss_type=2, detailed=True, effsize='np2',
                  correction='auto', between=None, within=None,
                  subject=None, group=None
                  )
```

```python
df = pd.DataFrame({'score': [64, 66, 68, 75, 78, 94, 98, 79, 71, 80,
                             91, 92, 93, 90, 97, 94, 82, 88, 95, 96,
                             79, 78, 88, 94, 92, 85, 83, 85, 82, 81],
                   'group': np.repeat(['strat1', 'strat2', 'strat3'],repeats=10)})
res = FuncMultiCmpt(pmc='auto',pair='unpaired',data=df, dv='score', factor='group', group='group')
res["APA"] 
# ['group:F(2, 17)=9.71719,p=0.0016']
```

#### FuncStars

```python
FuncStars(ax,
              pval=None,
              Ylim=None,
              Xlim=None,
              symbol='*',
              yscale=0.95,
              x1=0,
              x2=1,
              alpha=0.05,
              fontsize=14,
              fontsize_note=6,
              rotation=0,
              fontname='Arial',
              values_below=None,
              linego=True,
              linestyle='-',
              linecolor='k',
              linewidth=.8,
              nsshow='off',
              symbolcolor='k',
              tailindicator=[0.06, 0.06],
              report=None,
              report_scale=-0.1,
              report_loc=None)



```

### plots

#### stdshade

```python
stdshade(ax=None,*args, **kwargs)
```

#### add_colorbar

```python
add_colorbar(im, width=None, pad=None, **kwargs)
```

#### get_color

```python
get_color(n=1, cmap='auto')
```

```python
get_color(12)
# ['#474747',
#  '#FF2C00',
#  '#0C5DA5',
#  '#845B97',
#  '#58BBCC',
#  '#FF9500',
#  '#D57DBE',
#  '#474747',
#  '#FF2C00',
#  '#0C5DA5',
#  '#845B97',
#  '#58BBCC']
```

```python
get_color(5, cmap="jet") # ['#000080', '#000084', '#000089', '#00008d', '#000092']
get_color(5,cmap="rainbow") #['#8000ff', '#7e03ff', '#7c06ff', '#7a09ff', '#780dff']
```

#### img appearance

#### imgsets

```python
imgsets(
    img,
    sets=None,
    show=True,
    show_axis=False,
    size=None,
    dpi=100,
    figsize=None,
    auto=False,
    filter_kws=None,
)
```

```python
img = imgsets(
    fpath,
    sets={"rota": -5, "sharp": 10},
    dpi=200,
    # show_axis=True,
)
figsave(dir_save, "test1_sharp.pdf")


img2 = imgsets(
    fpath,
    sets={"rota": -5, "crop": [100, 100, 300, 400], "sharp": 10},
    dpi=200,
    filter_kws={
        "sharpen": 10,
    },
    # show_axis=True,
)
figsave(dir_save, "test2_crop.pdf")
```

```python
fload(dir_img)
```

![image-20240613233304196](./README.assets/image-20240613233304196.png)

```python
imgsets(img, sets={"color": 1.5}, show=0)
```

![image-20240613233356996](./README.assets/image-20240613233356996.png)

```python
imgsets(img, sets={"pad": (300, 300), "bgcolor": (73, 162, 127)}, show=0)
```

![image-20240613233423144](./README.assets/image-20240613233423144.png)

```python
imgsets(
    img,
    sets={"contrast": 1.3, "color": 1.5, "pad": (300, 300)},
    show=0,
    filter_kws=dict(sh=1050, EDG=10, gaus=5),
)
```

![image-20240613233503718](./README.assets/image-20240613233503718.png)

```python
imgsets(
    img,
    sets={"color": 10.5},
    show=0,
    filter_kws=dict(EDGE_ENHANCE=50, EDGE_NHANCEmore=50),
)
```

![image-20240613233525291](./README.assets/image-20240613233525291.png)

```python
imgsets(
    img,
    sets=dict(contr=1.5, rm="default"),
    show=0,
    # filter_kws=dict(sharp=1),
)
```

![image-20240613233554225](./README.assets/image-20240613233554225.png)

```python
imgsets(
    img,
    sets=dict(contr=0, rm="default"),
    show=0,
    filter_kws=dict(sharp=1),
)
```

![image-20240613233611627](./README.assets/image-20240613233611627.png)

#### figsets

```python
figsets(*args)
```

```python
cm = 1 / 2.54
# plt.style.use("paper")
plt.figure(figsize=[8 * cm, 5 * cm])
for i in range(2, 4):
    plt.plot(x, y * i, ls="-")
figsets(
    plt.gca(),
    {
        "xlabel": f"time([{x[0]}:{x[-1]}])",
        "ylabel": "Amplitude (signals)",
        # "titel": "paper",
        "xlim": [0, 600],
        "xtick": np.arange(0, 620, 150),
        "xlabel": "test xticklabel",
        # "ylim": [-2.5, 2.5],
        "sp": "go",
        # "style": "paper",
        "box": ":",
        "grid": "on",
        "minorticks": "on",
        "ticks": {"c": "k"},
    },
)
figsets('style','paper')
```

```python
cm = 1/2.54  # centimeters in inches
fig, ax = plt.subplots(1, 1, figsize=(7*cm, 5*cm))
x = np.linspace(0, 2 * np.pi, 50) * 100
y = np.sin(x)
c=get_color(7)

for i in range(2,7):
    plt.plot(x, y*i,c=c[i])
figsets(
    ax,
    {
        "xlim": [0, 450],
        # "ylim": [-1.5, 1.5],
        "xlabel": "2222",
        # "style":"paper",
        "yticks": np.arange(-5,5, 2),
        "ylabel": "ylabelsssss",
        "xtkbel": range(0, 800, 100),
        # "spine": 5,
        "suptitle": "supertitle",
        # "minorticks": "y",
        # "ticksloc":"lt",
        # "ticks": {"direction": "out",'c':'b'},
        "rotation":45,
        # 'box':"lt",
        # "labellocation":'r',
        # "ax_color":'b',
        # 'grid':{"which":'minor','lw':1,"ls":'-.','c':'b','al':0.3},
    },
)
```

