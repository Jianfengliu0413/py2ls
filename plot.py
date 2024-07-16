from scipy.signal import savgol_filter
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck 
import seaborn as sns
from cycler import cycler


def read_mplstyle(style_file):
    # Load the style file
    plt.style.use(style_file)

    # Get the current style properties
    style_dict = plt.rcParams

    # Convert to dictionary
    style_dict = dict(style_dict)
    # Print the style dictionary
    for i, j in style_dict.items():
        print(f"\n{i}::::{j}")
    return style_dict
# #example usage:
# style_file = "/ std-colors.mplstyle"
# style_dict = read_mplstyle(style_file)


# set up the colorlist, give the number, or the colormap's name
def get_color(n=1, cmap="auto", how="start"):
    # Extract the colormap as a list
    def cmap2hex(cmap_name):
        cmap_ = matplotlib.pyplot.get_cmap(cmap_name)
        colors = [cmap_(i) for i in range(cmap_.N)]
        return [matplotlib.colors.rgb2hex(color) for color in colors]
        # usage: clist = cmap2hex("viridis")
    # cycle times, total number is n (defaultn=10)
    def cycle2list(colorlist, n=10):
        cycler_ = cycler(tmp=colorlist)
        clist = []
        for i, c_ in zip(range(n), cycler_()):
            clist.append(c_["tmp"])
            if i > n:
                break
        return clist
    def hue2rgb(hex_colors):
        def hex_to_rgb(hex_color):
            """Converts a hexadecimal color code to RGB values."""
            if hex_colors.startswith("#"):
                hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        if isinstance(hex_colors, str):
            return hex_to_rgb(hex_colors)
        elif isinstance(hex_colors, (list)):
            """Converts a list of hexadecimal color codes to a list of RGB values."""
            rgb_values = [hex_to_rgb(hex_color) for hex_color in hex_colors]
            return rgb_values
    if "aut" in cmap:
        colorlist = [
            "#474747",
            "#FF2C00",
            "#0C5DA5",
            "#845B97",
            "#58BBCC",
            "#FF9500",
            "#D57DBE",
        ]
    else:
        colorlist = cmap2hex(cmap)
    if "st" in how.lower() or "be" in how.lower():
        # cycle it
        clist = cycle2list(colorlist, n=n)
    if "l" in how.lower() or "p" in how.lower():
        clist = []
        [
            clist.append(colorlist[i])
            for i in [int(i) for i in np.linspace(0, len(colorlist) - 1, n)]
        ]

    return clist  # a color list
    # example usage: clist = get_color(4,cmap="auto", how="start") # get_color(4, cmap="hot", how="linspace")

""" 
    # n = 7
    # clist = get_color(n, cmap="auto", how="linspace")  # get_color(100)
    # plt.figure(figsize=[8, 5], dpi=100)
    # x = np.linspace(0, 2 * np.pi, 50) * 100
    # y = np.sin(x)
    # for i in range(1, n + 1):
    #     plt.plot(x, y + i, c=clist[i - 1], lw=5, label=str(i))
    # plt.legend()
    # plt.ylim(-2, 20)
    # figsets(plt.gca(), {"style": "whitegrid"}) """

def stdshade(ax=None,*args, **kwargs):
    # Separate kws_line and kws_fill if necessary
    kws_line = kwargs.pop('kws_line', {})
    kws_fill = kwargs.pop('kws_fill', {})

    # Merge kws_line and kws_fill into kwargs
    kwargs.update(kws_line)
    kwargs.update(kws_fill)
    def str2list(str_):
        l = []
        [l.append(x) for x in str_]
        return l
    def hue2rgb(hex_colors):
        def hex_to_rgb(hex_color):
            """Converts a hexadecimal color code to RGB values."""
            if hex_colors.startswith("#"):
                hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        if isinstance(hex_colors, str):
            return hex_to_rgb(hex_colors)
        elif isinstance(hex_colors, (list)):
            """Converts a list of hexadecimal color codes to a list of RGB values."""
            rgb_values = [hex_to_rgb(hex_color) for hex_color in hex_colors]
            return rgb_values
    if (
        isinstance(ax, np.ndarray)
        and ax.ndim == 2
        and min(ax.shape) > 1
        and max(ax.shape) > 1
    ):
        y = ax
        ax = plt.gca()
    if ax is None:
        ax = plt.gca()
    alpha = 0.5
    acolor = "k"
    paraStdSem = "sem"
    plotStyle = "-"
    plotMarker = "none"
    smth = 1
    l_c_one = ["r", "g", "b", "m", "c", "y", "k", "w"]
    l_style2 = ["--", "-."]
    l_style1 = ["-", ":"]
    l_mark = ["o", "+", "*", ".", "x", "_", "|", "s", "d", "^", "v", ">", "<", "p", "h"]
    # Check each argument
    for iarg in range(len(args)):
        if (
            isinstance(args[iarg], np.ndarray)
            and args[iarg].ndim == 2
            and min(args[iarg].shape) > 1
            and max(args[iarg].shape) > 1
        ):
            y = args[iarg]
        # Except y, continuous data is 'F'
        if (isinstance(args[iarg], np.ndarray) and args[iarg].ndim == 1) or isinstance(
            args[iarg], range
        ):
            x = args[iarg]
            if isinstance(x, range):
                x = np.arange(start=x.start, stop=x.stop, step=x.step)
        # Only one number( 0~1), 'alpha' / color
        if isinstance(args[iarg], (int, float)):
            if np.size(args[iarg]) == 1 and 0 <= args[iarg] <= 1:
                alpha = args[iarg]
        if isinstance(args[iarg], (list, tuple)) and np.size(args[iarg]) == 3:
            acolor = args[iarg]
            acolor = tuple(acolor) if isinstance(acolor, list) else acolor
        # Color / plotStyle /
        if (
            isinstance(args[iarg], str)
            and len(args[iarg]) == 1
            and args[iarg] in l_c_one
        ):
            acolor = args[iarg]
        else:
            if isinstance(args[iarg], str):
                if args[iarg] in ["sem", "std"]:
                    paraStdSem = args[iarg]
                if args[iarg].startswith("#"):
                    acolor=hue2rgb(args[iarg])
                if str2list(args[iarg])[0] in l_c_one:
                    if len(args[iarg]) == 3:
                        k = [i for i in str2list(args[iarg]) if i in l_c_one]
                        if k != []:
                            acolor = k[0] 
                        st = [i for i in l_style2 if i in args[iarg]]
                        if st != []:
                            plotStyle = st[0] 
                    elif len(args[iarg]) == 2:
                        k = [i for i in str2list(args[iarg]) if i in l_c_one]
                        if k != []:
                            acolor = k[0] 
                        mk = [i for i in str2list(args[iarg]) if i in l_mark]
                        if mk != []:
                            plotMarker = mk[0] 
                        st = [i for i in l_style1 if i in args[iarg]]
                        if st != []:
                            plotStyle = st[0] 
                if len(args[iarg]) == 1:
                    k = [i for i in str2list(args[iarg]) if i in l_c_one]
                    if k != []:
                        acolor = k[0] 
                    mk = [i for i in str2list(args[iarg]) if i in l_mark]
                    if mk != []:
                        plotMarker = mk[0] 
                    st = [i for i in l_style1 if i in args[iarg]]
                    if st != []:
                        plotStyle = st[0] 
                if len(args[iarg]) == 2:
                    st = [i for i in l_style2 if i in args[iarg]]
                    if st != []:
                        plotStyle = st[0]
        # smth
        if (
            isinstance(args[iarg], (int, float))
            and np.size(args[iarg]) == 1
            and args[iarg] >= 1
        ):
            smth = args[iarg]
    smth = kwargs.get('smth', smth)
    if "x" not in locals() or x is None:
        x = np.arange(1, y.shape[1] + 1)
    elif len(x) < y.shape[1]:
        y = y[:, x]
        nRow = y.shape[0]
        nCol = y.shape[1]
        print(f"y was corrected, please confirm that {nRow} row, {nCol} col")
    else:
        x = np.arange(1, y.shape[1] + 1)

    if x.shape[0] != 1:
        x = x.T
    yMean = np.nanmean(y, axis=0)
    if smth > 1:
        yMean = savgol_filter(np.nanmean(y, axis=0), smth, 1)
    else:
        yMean = np.nanmean(y, axis=0)
    if paraStdSem == "sem":
        if smth > 1:
            wings = savgol_filter(np.nanstd(y, axis=0) / np.sqrt(y.shape[0]), smth, 1)
        else:
            wings = np.nanstd(y, axis=0) / np.sqrt(y.shape[0])
    elif paraStdSem == "std":
        if smth > 1:
            wings = savgol_filter(np.nanstd(y, axis=0), smth, 1)
        else:
            wings = np.nanstd(y, axis=0)

    # fill_kws = kwargs.get('fill_kws', {})
    # line_kws = kwargs.get('line_kws', {})

    # setting form kwargs
    lw = kwargs.get('lw', 1.5)
    ls= kwargs.get('ls', plotStyle)
    marker=kwargs.get("marker",plotMarker)
    label=kwargs.get("label",None)
    label_line = kwargs.get("label_line",None)
    label_fill = kwargs.get('label_fill',None)
    alpha=kwargs.get('alpha',alpha)
    color=kwargs.get('color', acolor)
    if not label_line and label:
        label_line = label
    kwargs['lw'] = lw
    kwargs['ls'] = ls
    kwargs['label_line'] = label_line
    kwargs['label_fill'] = label_fill

    # set kws_line
    if 'color' not in kws_line:
        kws_line['color']=color
    if 'lw' not in kws_line:
        kws_line['lw']=lw
    if 'ls' not in kws_line:
        kws_line['ls']=ls
    if 'marker' not in kws_line:
        kws_line['marker']=marker
    if 'label' not in kws_line:
        kws_line['label']=label_line

    # set kws_line
    if 'color' not in kws_fill:
        kws_fill['color']=color
    if 'alpha' not in kws_fill:
        kws_fill['alpha']=alpha
    if 'lw' not in kws_fill:
        kws_fill['lw']=0
    if 'label' not in kws_fill:
        kws_fill['label']=label_fill

    fill = ax.fill_between(x, yMean + wings, yMean - wings, **kws_fill)
    line = ax.plot(x, yMean, **kws_line)
    return line[0], fill


"""
########## Usage 1 ##########
plot.stdshade(data,
              'b',
              ':',
              'd',
              0.1,
              4,
              label='ddd',
              label_line='label_line',
              label_fill="label-fill")
plt.legend()

########## Usage 2 ##########
plot.stdshade(data,
              'm-',
              alpha=0.1,
              lw=2,
              ls=':',
              marker='d',
              color='b',
              smth=4,
              label='ddd',
              label_line='label_line',
              label_fill="label-fill")
plt.legend()

"""

def adjust_spines(ax=None, spines=['left', 'bottom'],distance=2):
    if ax is None:
        ax = plt.gca()
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', distance))  # outward by 2 points
            # spine.set_smart_bounds(True)
        else:
            spine.set_color('none')  # don't draw spine
    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        ax.yaxis.set_ticks([])
    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])
# And then plot the data:
def figsets(*args):
    fig = plt.gcf()
    fontsize = 11
    fontname = "Arial"
    sns_themes = ["white", "whitegrid", "dark", "darkgrid", "ticks"]
    sns_contexts = ["notebook", "talk", "poster"]  # now available "paper"
    scienceplots_styles = ["science","nature",
        "scatter","ieee","no-latex","std-colors","high-vis","bright","dark_background","science",
        "high-vis","vibrant","muted","retro","grid","high-contrast","light","cjk-tc-font","cjk-kr-font",
    ]
    def sets_priority(ax,key, value):
        if ("fo" in key) and (("size" in key) or ("sz" in key)):
            fontsize=value
            plt.rcParams.update({"font.size": value})
        # style
        if "st" in key.lower() or "th" in key.lower():
            if isinstance(value, str):
                if (value in plt.style.available) or (value in scienceplots_styles):
                    plt.style.use(value)
                elif value in sns_themes:
                    sns.set_style(value)
                elif value in sns_contexts:
                    sns.set_context(value)
                else:
                    print(
                        f"\nWarning\n'{value}' is not a plt.style,select on below:\n{plt.style.available+sns_themes+sns_contexts+scienceplots_styles}"
                    )
            if isinstance(value, list):
                for i in value:
                    if (i in plt.style.available) or (i in scienceplots_styles):
                        plt.style.use(i)
                    elif i in sns_themes:
                        sns.set_style(i)
                    elif i in sns_contexts:
                        sns.set_context(i)
                    else:
                        print(
                            f"\nWarning\n'{i}' is not a plt.style,select on below:\n{plt.style.available+sns_themes+sns_contexts+scienceplots_styles}"
                        )
        if "la" in key.lower():
            if "loc" in key.lower() or "po" in key.lower():
                for i in value:
                    if "l" in i.lower():
                        ax.yaxis.set_label_position("left")
                    if "r" in i.lower():
                        ax.yaxis.set_label_position("right")
                    if "t" in i.lower():
                        ax.xaxis.set_label_position("top")
                    if "b" in i.lower():
                        ax.xaxis.set_label_position("bottom")
            if ("x" in key.lower()) and (
                "tic" not in key.lower() and "tk" not in key.lower()
            ):
                ax.set_xlabel(value, fontname=fontname)
            if ("y" in key.lower()) and (
                "tic" not in key.lower() and "tk" not in key.lower()
            ):
                ax.set_ylabel(value, fontname=fontname)
            if ("z" in key.lower()) and (
                "tic" not in key.lower() and "tk" not in key.lower()
            ):
                ax.set_zlabel(value, fontname=fontname)
        # tick location
        if "tic" in key.lower() or "tk" in key.lower():
            if ("loc" in key.lower()) or ("po" in key.lower()):
                if isinstance(value,str):
                    value=[value]
                if isinstance(value, list):
                    loc = []
                    for i in value:
                        if ("l" in i.lower()) and ("a" not in i.lower()):
                            ax.yaxis.set_ticks_position("left")
                        if "r" in i.lower():
                            ax.yaxis.set_ticks_position("right")
                        if "t" in i.lower():
                            ax.xaxis.set_ticks_position("top")
                        if "b" in i.lower():
                            ax.xaxis.set_ticks_position("bottom")
                        if i.lower() in ["a", "both", "all", "al", ":"]:
                            ax.xaxis.set_ticks_position("both")
                            ax.yaxis.set_ticks_position("both")
                        if i.lower() in ["xnone",'xoff',"none"]:
                            ax.xaxis.set_ticks_position("none")
                        if i.lower() in ["ynone",'yoff','none']:
                            ax.yaxis.set_ticks_position("none")
            # ticks / labels
            elif "x" in key.lower():
                if value is None:
                    value=[]
                if "la" not in key.lower():
                    ax.set_xticks(value)
                if "la" in key.lower():
                    ax.set_xticklabels(value)
            elif "y" in key.lower():
                if value is None:
                    value=[]
                if "la" not in key.lower():
                    ax.set_yticks(value)
                if "la" in key.lower():
                    ax.set_yticklabels(value)
            elif "z" in key.lower():
                if value is None:
                    value=[]
                if "la" not in key.lower():
                    ax.set_zticks(value)
                if "la" in key.lower():
                    ax.set_zticklabels(value)
        # rotation
        if "angle" in key.lower() or ("rot" in key.lower()):
            if "x" in key.lower():
                ax.tick_params(axis="x", rotation=value)
            if "y" in key.lower():
                ax.tick_params(axis="y", rotation=value)

        if "bo" in key in key:  # and ("p" in key or "l" in key):
                # print("'ticks' style is recommended")
            if isinstance(value, (str, list)):
                locations = []
                for i in value:
                    if "l" in i.lower():
                        locations.append("left")
                    if "r" in i.lower():
                        locations.append("right")
                    if "t" in i.lower():
                        locations.append("top")
                    if "b" in i.lower():
                        locations.append("bottom")
                    if i.lower() in ["a", "both", "all", "al", ":"]:
                        [
                            locations.append(x)
                            for x in ["left", "right", "top", "bottom"]
                        ]
                for i in value:
                    if i.lower() in "none":
                        locations = []
                # check spines
                for loc, spi in ax.spines.items():
                    if loc in locations:
                        spi.set_position(("outward", 0))
                    else:
                        spi.set_color("none")  # no spine
        if key == "tick" or key == "ticks" or key == "ticks_para":
            if isinstance(value, dict):
                for k, val in value.items():
                    if "wh" in k.lower():
                        ax.tick_params(
                            which=val
                        )  # {'major', 'minor', 'both'}, default: 'major'
                    elif "dir" in k.lower():
                        ax.tick_params(direction=val)  # {'in', 'out', 'inout'}
                    elif "len" in k.lower():
                        ax.tick_params(length=val)
                    elif ("wid" in k.lower()) or ("wd" in k.lower()):
                        ax.tick_params(width=val)
                    elif "ax" in k.lower():
                        ax.tick_params(axis=val)  # {'x', 'y', 'both'}, default: 'both'
                    elif ("c" in k.lower()) and ("ect" not in k.lower()):
                        ax.tick_params(colors=val)  # Tick color.
                    elif "pad" in k.lower():
                        ax.tick_params(
                            pad=val
                        )  # float, distance in points between tick and label
                    elif (
                        ("lab" in k.lower())
                        and ("s" in k.lower())
                        and ("z" in k.lower())
                    ):
                        ax.tick_params(
                            labelsize=val
                        )  # float, distance in points between tick and label

        if "mi" in key.lower() and "tic" in key.lower():
            if "x" in value.lower() or "x" in key.lower():
                ax.xaxis.set_minor_locator(tck.AutoMinorLocator())  # ax.minorticks_on()
            if "y" in value.lower() or "y" in key.lower():
                ax.yaxis.set_minor_locator(
                    tck.AutoMinorLocator()
                )  # ax.minorticks_off()
            if value.lower() in ["both", ":", "all", "a", "b", "on"]:
                ax.minorticks_on()
        if key == "colormap" or key == "cmap":
            plt.set_cmap(value)
    def sets_small(ax,key, value):
        if key == "figsize":
            pass
        if key == "xlim":
            ax.set_xlim(value)
        if key == "ylim":
            ax.set_ylim(value)
        if key == "zlim":
            ax.set_zlim(value)
        if "sc" in key.lower():
            if "x" in key.lower():
                ax.set_xscale(value)
            if "y" in key.lower():
                ax.set_yscale(value)
            if "z" in key.lower():
                ax.set_zscale(value)
        if key == "grid":
            if isinstance(value, dict):
                for k, val in value.items():
                    if "wh" in k.lower():
                        ax.grid(
                            which=val
                        )  # {'major', 'minor', 'both'}, default: 'major'
                    elif "ax" in k.lower():
                        ax.grid(axis=val)  # {'x', 'y', 'both'}, default: 'both'
                    elif ("c" in k.lower()) and ("ect" not in k.lower()):
                        ax.grid(color=val)  # Tick color.
                    elif "l" in k.lower() and ("s" in k.lower()):
                        ax.grid(linestyle=val)
                    elif "l" in k.lower() and ("w" in k.lower()):
                        ax.grid(linewidth=val)
                    elif "al" in k.lower():
                        ax.grid(alpha=val)
            else:
                if value == "on" or value is True:
                    ax.grid(visible=True)
                elif value == "off" or value is False:
                    ax.grid(visible=False)
        if "tit" in key.lower():
            if "sup" in key.lower():
                plt.suptitle(value)
            else:
                ax.set_title(value)
        if key.lower() in ["spine", "adjust", "ad", "sp", "spi", "adj","spines"]:
            if isinstance(value, bool) or (value in ["go", "do", "ja", "yes"]):
                if value:
                    adjust_spines(ax)  # dafault distance=2
            if isinstance(value, (float, int)):
                adjust_spines(ax=ax, distance=value)
        if "c" in key.lower() and ("sp" in key.lower() or "ax" in key.lower()):
            for loc, spi in ax.spines.items():
                spi.set_color(value)

    for arg in args:
        if isinstance(arg,matplotlib.axes._axes.Axes):
            ax=arg
            args=args[1:]
    if 'ax' not in locals():
        ax=plt.gca()

    for arg in args:
        if isinstance(arg, dict):
            for k, val in arg.items():
                sets_priority(ax,k, val)
            for k, val in arg.items():
                sets_small(ax,k, val)
        else:
            Nargin = len(args) // 2
            ax.labelFontSizeMultiplier = 1
            ax.titleFontSizeMultiplier = 1
            ax.set_facecolor("w")

            for ip in range(Nargin):
                key = args[ip * 2].lower()
                value = args[ip * 2 + 1]
                sets_priority(ax,key, value)
            for ip in range(Nargin):
                key = args[ip * 2].lower()
                value = args[ip * 2 + 1]
                sets_small(ax,key, value)
    colors = [
        "#474747",
        "#FF2C00",
        "#0C5DA5",
        "#845B97",
        "#58BBCC",
        "#FF9500",
        "#D57DBE",
    ]
    matplotlib.rcParams["axes.prop_cycle"] = cycler(color=colors)
    if len(fig.get_axes()) > 1:
        plt.tight_layout()
        plt.gcf().align_labels()


def figsave(*args,dpi=300):
    dir_save = None
    fname = None 
    for arg in args:
        if isinstance(arg, str):
            if '/' in arg or '\\' in arg:
                dir_save = arg
            elif '/' not in arg and '\\' not in arg:
                fname = arg
    # Backup original values
    if '/' in dir_save:
        if dir_save[-1] != '/':
            dir_save = dir_save + '/'
    elif '\\' in dir_save:
        if dir_save[-1] != '\\':
            dir_save = dir_save + '\\'
    else:
        raise ValueError('Check the Path of dir_save Directory')
    ftype = fname.split('.')[-1]
    if len(fname.split('.')) == 1:
        ftype = 'nofmt'
        fname = dir_save + fname + '.' + ftype
    else:
        fname = dir_save + fname
    # Save figure based on file type
    if ftype.lower() == 'eps':
        plt.savefig(fname, format='eps', bbox_inches='tight')
        plt.savefig(fname.replace('.eps', '.pdf'),
                    format='pdf', bbox_inches='tight',dpi=dpi)
    elif ftype.lower() == 'nofmt': # default: both "tif" and "pdf"
        fname_corr=fname.replace('nofmt','pdf')
        plt.savefig(fname_corr, format='pdf', bbox_inches='tight',dpi=dpi)
        fname=fname.replace('nofmt','tif')
        plt.savefig(fname, format='tiff', dpi=dpi, bbox_inches='tight')
        print(f"default saving filetype: both 'tif' and 'pdf")
    elif ftype.lower() == 'pdf':
        plt.savefig(fname, format='pdf', bbox_inches='tight',dpi=dpi)
    elif ftype.lower() in ['jpg', 'jpeg']:
        plt.savefig(fname, format='jpeg', dpi=dpi, bbox_inches='tight')
    elif ftype.lower() == 'png':
        plt.savefig(fname, format='png', dpi=dpi,
                    bbox_inches='tight', transparent=True)
    elif ftype.lower() in ['tiff', 'tif']:
        plt.savefig(fname, format='tiff', dpi=dpi, bbox_inches='tight')
    elif ftype.lower() == 'emf':
        plt.savefig(fname, format='emf', dpi=dpi, bbox_inches='tight')
    elif ftype.lower() == 'fig':
        plt.savefig(fname, format='pdf', bbox_inches='tight',dpi=dpi)
    print(f'\nSaved @: dpi={dpi}\n{fname}')