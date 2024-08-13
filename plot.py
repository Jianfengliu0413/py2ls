import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba
from scipy.stats import gaussian_kde
import seaborn as sns
import matplotlib
import matplotlib.ticker as tck
from cycler import cycler
import logging
import os
from .ips import fsave, fload, mkdir
from .stats import *

# Suppress INFO messages from fontTools
logging.getLogger("fontTools").setLevel(logging.WARNING)


def catplot(data, *args, **kwargs):
    """
    catplot(data, opt=None, ax=None)
    The catplot function is designed to provide a flexible way to create various types of
    categorical plots. It supports multiple plot layers such as bars, error bars, scatter
    plots, box plots, violin plots, and lines. Each plot type is handled by its own internal
    function, allowing for separation of concerns and modularity in the design.
    Args:
        data (array): data matrix
    """

    def plot_bars(data, data_m, opt_b, xloc, ax, label=None):
        bar_positions = get_positions(
            xloc, opt_b["loc"], opt_b["x_width"], data.shape[0]
        )
        bar_positions = np.nanmean(bar_positions, axis=0)
        for i, (x, y) in enumerate(zip(bar_positions, data_m)):
            color = to_rgba(opt_b["FaceColor"][i % len(opt_b["FaceColor"])])
            if label is not None and i < len(label):
                ax.bar(
                    x,
                    y,
                    width=opt_b["x_width"],
                    color=color,
                    edgecolor=opt_b["EdgeColor"],
                    alpha=opt_b["FaceAlpha"],
                    linewidth=opt_b["LineWidth"],
                    hatch=opt_b["hatch"],
                    label=label[i],
                )
            else:
                ax.bar(
                    x,
                    y,
                    width=opt_b["x_width"],
                    color=color,
                    edgecolor=opt_b["EdgeColor"],
                    alpha=opt_b["FaceAlpha"],
                    linewidth=opt_b["LineWidth"],
                    hatch=opt_b["hatch"],
                )

    def plot_errors(data, data_m, opt_e, xloc, ax, label=None):
        error_positions = get_positions(
            xloc, opt_e["loc"], opt_e["x_width"], data.shape[0]
        )
        error_positions = np.nanmean(error_positions, axis=0)
        errors = np.nanstd(data, axis=0, ddof=1)
        if opt_e["error"] == "sem":
            errors /= np.sqrt(np.sum(~np.isnan(data), axis=0))

        if not isinstance(opt_e["FaceColor"], list):
            opt_e["FaceColor"] = [opt_e["FaceColor"]]
        if not isinstance(opt_e["MarkerEdgeColor"], list):
            opt_e["MarkerEdgeColor"] = [opt_e["MarkerEdgeColor"]]
        for i, (x, y, err) in enumerate(zip(error_positions, data_m, errors)):
            if label is not None and i < len(label):
                if opt_e["MarkerSize"] == "auto":
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                        label=label[i],
                    )
                else:
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        markersize=opt_e["MarkerSize"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                        label=label[i],
                    )
            else:
                if opt_e["MarkerSize"] == "auto":
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                    )
                else:
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        markersize=opt_e["MarkerSize"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                    )

    def plot_scatter(data, opt_s, xloc, ax, label=None):
        scatter_positions = get_positions(
            xloc, opt_s["loc"], opt_s["x_width"], data.shape[0]
        )
        for i, (x, y) in enumerate(zip(scatter_positions.T, data.T)):
            color = to_rgba(opt_s["FaceColor"][i % len(opt_s["FaceColor"])])
            if label is not None and i < len(label):
                ax.scatter(
                    x,
                    y,
                    color=color,
                    alpha=opt_s["FaceAlpha"],
                    edgecolor=opt_s["MarkerEdgeColor"],
                    s=opt_s["MarkerSize"],
                    marker=opt_s["Marker"],
                    linewidths=opt_s["LineWidth"],
                    cmap=opt_s["cmap"],
                    label=label[i],
                )
            else:
                ax.scatter(
                    x,
                    y,
                    color=color,
                    alpha=opt_s["FaceAlpha"],
                    edgecolor=opt_s["MarkerEdgeColor"],
                    s=opt_s["MarkerSize"],
                    marker=opt_s["Marker"],
                    linewidths=opt_s["LineWidth"],
                    cmap=opt_s["cmap"],
                )

    def plot_boxplot(data, bx_opt, xloc, ax, label=None):
        if "l" in bx_opt["loc"]:
            X_bx = xloc - bx_opt["x_width"]
        elif "r" in bx_opt["loc"]:
            X_bx = xloc + bx_opt["x_width"]
        elif "i" in bx_opt["loc"]:
            X_bx = xloc
            X_bx[:, 0] += bx_opt["x_width"]
            X_bx[:, -1] -= bx_opt["x_width"]
        elif "o" in bx_opt["loc"]:
            X_bx = xloc
            X_bx[:, 0] -= bx_opt["x_width"]
            X_bx[:, -1] += bx_opt["x_width"]
        elif "c" in bx_opt["loc"] or "m" in bx_opt["loc"]:
            X_bx = xloc
        else:
            X_bx = xloc

        boxprops = dict(color=bx_opt["EdgeColor"], linewidth=bx_opt["BoxLineWidth"])
        flierprops = dict(
            marker=bx_opt["OutlierMarker"],
            markerfacecolor=bx_opt["OutlierColor"],
            markersize=bx_opt["OutlierSize"],
        )
        whiskerprops = dict(
            linestyle=bx_opt["WhiskerLineStyle"],
            color=bx_opt["WhiskerLineColor"],
            linewidth=bx_opt["WhiskerLineWidth"],
        )
        capprops = dict(
            color=bx_opt["CapLineColor"],
            linewidth=bx_opt["CapLineWidth"],
        )
        medianprops = dict(
            linestyle=bx_opt["MedianLineStyle"],
            color=bx_opt["MedianLineColor"],
            linewidth=bx_opt["MedianLineWidth"],
        )
        meanprops = dict(
            linestyle=bx_opt["MeanLineStyle"],
            color=bx_opt["MeanLineColor"],
            linewidth=bx_opt["MeanLineWidth"],
        )
        # MeanLine or MedianLine only keep only one
        if bx_opt["MeanLine"]:  # MeanLine has priority
            bx_opt["MedianLine"] = False
        # rm NaNs
        cleaned_data = [data[~np.isnan(data[:, i]), i] for i in range(data.shape[1])]

        bxp = ax.boxplot(
            cleaned_data,
            positions=X_bx,
            notch=bx_opt["Notch"],
            patch_artist=True,
            boxprops=boxprops,
            flierprops=flierprops,
            whiskerprops=whiskerprops,
            capwidths=bx_opt["CapSize"],
            showfliers=bx_opt["Outliers"],
            showcaps=bx_opt["Caps"],
            capprops=capprops,
            medianprops=medianprops,
            meanline=bx_opt["MeanLine"],
            showmeans=bx_opt["MeanLine"],
            meanprops=meanprops,
            widths=bx_opt["x_width"],
            label=label,
        )
        if not bx_opt["MedianLine"]:
            for median in bxp["medians"]:
                median.set_visible(False)

        if bx_opt["BoxLineWidth"] < 0.1:
            bx_opt["EdgeColor"] = "none"
        else:
            bx_opt["EdgeColor"] = bx_opt["EdgeColor"]

        for patch, color in zip(bxp["boxes"], bx_opt["FaceColor"]):
            patch.set_facecolor(to_rgba(color, bx_opt["FaceAlpha"]))

        if bx_opt["MedianLineTop"]:
            ax.set_children(ax.get_children()[::-1])  # move median line forward

    def plot_violin(data, opt_v, xloc, ax, label=None):
        violin_positions = get_positions(
            xloc, opt_v["loc"], opt_v["x_width"], data.shape[0]
        )
        violin_positions = np.nanmean(violin_positions, axis=0)
        for i, (x, ys) in enumerate(zip(violin_positions, data.T)):
            ys = ys[~np.isnan(ys)]
            kde = gaussian_kde(ys, bw_method=opt_v["BandWidth"])
            min_val, max_val = ys.min(), ys.max()
            y_vals = np.linspace(min_val, max_val, opt_v["NumPoints"])
            kde_vals = kde(y_vals)
            kde_vals = kde_vals / kde_vals.max() * opt_v["x_width"]
            if label is not None and i < len(label):
                if len(ys) > 1:
                    if "r" in opt_v["loc"].lower():
                        ax.fill_betweenx(
                            y_vals,
                            x,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            label=label[i],
                        )
                    elif (
                        "l" in opt_v["loc"].lower() and not "f" in opt_v["loc"].lower()
                    ):
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            label=label[i],
                        )
                    elif "o" in opt_v["loc"].lower() or "both" in opt_v["loc"].lower():
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            label=label[i],
                        )
                    elif "i" in opt_v["loc"].lower():
                        if i % 2 == 1:  # odd number
                            ax.fill_betweenx(
                                y_vals,
                                x - kde_vals,
                                x,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                label=label[i],
                            )
                        else:
                            ax.fill_betweenx(
                                y_vals,
                                x,
                                x + kde_vals,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                label=label[i],
                            )
                    elif "f" in opt_v["loc"].lower():
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            label=label[i],
                        )
            else:
                if "r" in opt_v["loc"].lower():
                    ax.fill_betweenx(
                        y_vals,
                        x,
                        x + kde_vals,
                        color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                        alpha=opt_v["FaceAlpha"],
                        edgecolor=opt_v["EdgeColor"],
                    )
                elif "l" in opt_v["loc"].lower() and not "f" in opt_v["loc"].lower():
                    ax.fill_betweenx(
                        y_vals,
                        x - kde_vals,
                        x,
                        color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                        alpha=opt_v["FaceAlpha"],
                        edgecolor=opt_v["EdgeColor"],
                    )
                elif "o" in opt_v["loc"].lower() or "both" in opt_v["loc"].lower():
                    ax.fill_betweenx(
                        y_vals,
                        x - kde_vals,
                        x + kde_vals,
                        color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                        alpha=opt_v["FaceAlpha"],
                        edgecolor=opt_v["EdgeColor"],
                    )
                elif "i" in opt_v["loc"].lower():
                    if i % 2 == 1:  # odd number
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                        )
                    else:
                        ax.fill_betweenx(
                            y_vals,
                            x,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                        )
                elif "f" in opt_v["loc"].lower():
                    ax.fill_betweenx(
                        y_vals,
                        x - kde_vals,
                        x + kde_vals,
                        color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                        alpha=opt_v["FaceAlpha"],
                        edgecolor=opt_v["EdgeColor"],
                    )

    def plot_lines(data, opt_l, opt_s, ax):
        scatter_positions = get_positions(
            xloc, opt_s["loc"], opt_s["x_width"], data.shape[0]
        )
        for incol in range(data.shape[1] - 1):
            for irow in range(data.shape[0]):
                if not np.isnan(data[irow, incol]):
                    if (
                        opt_l["LineStyle"] is not None
                        and not opt_l["LineStyle"] == "none"
                    ):
                        x_data = [
                            scatter_positions[irow, incol],
                            scatter_positions[irow, incol + 1],
                        ]
                        y_data = [data[irow, incol], data[irow, incol + 1]]

                        ax.plot(
                            x_data,
                            y_data,
                            color=opt_l["LineColor"],
                            linestyle=opt_l["LineStyle"],
                            linewidth=opt_l["LineWidth"],
                            alpha=opt_l["LineAlpha"],
                        )

    def get_positions(xloc, loc_type, x_width, n_row=None):
        if "rand" in loc_type:
            scatter_positions = np.zeros((n_row, len(xloc)))
            np.random.seed(111)
            for i, x in enumerate(xloc):
                scatter_positions[:, i] = np.random.uniform(
                    x - x_width, x + x_width, n_row
                )
            return scatter_positions
        elif "l" in loc_type:
            return np.tile(xloc - x_width, (n_row, 1))
        elif "r" in loc_type and not "d" in loc_type:
            return np.tile(xloc + x_width, (n_row, 1))
        elif "i" in loc_type:
            return np.tile(
                np.concatenate([xloc[:1] + x_width, xloc[1:-1], xloc[-1:] - x_width]),
                (n_row, 1),
            )
        elif "o" in loc_type:
            return np.tile(
                np.concatenate([xloc[:1] - x_width, xloc[1:-1], xloc[-1:] + x_width]),
                (n_row, 1),
            )
        else:
            return np.tile(xloc, (n_row, 1))

    def sort_catplot_layers(custom_order, full_order=["b", "bx", "e", "v", "s", "l"]):
        """
        sort layers
        """
        # Ensure custom_order is a list of strings
        custom_order = [str(layer) for layer in custom_order]
        j = 1
        layers = list(range(len(full_order)))
        for i in range(len(full_order)):
            if full_order[i] not in custom_order:
                layers[i] = i
            else:
                layers[i] = None
        j = 0
        for i in range(len(layers)):
            if layers[i] is None:
                full_order[i] = custom_order[j]
                j += 1
        return full_order
        # # Example usage:
        # custom_order = ['s', 'bx', 'e']
        # full_order = sort_catplot_layers(custom_order)

    ax = kwargs.get("ax", None)

    col = kwargs.get("col", None)
    if not col:
        if "ax" not in locals() or ax is None:
            ax = plt.gca()
        # figsets
        kw_figsets = kwargs.get("figsets", None)
        # if kw_figsets:
        #     ylim_tmp=kw_figsets.get("ylim",None)
        # if ylim_tmp:
        #     ax.set_ylim(ylim_tmp)
        # check the data type
        if isinstance(data, pd.DataFrame):
            df = data.copy()
            x = kwargs.get("x", None)
            y = kwargs.get("y", None)
            hue = kwargs.get("hue", None)
            data = df2array(data=data, x=x, y=y, hue=hue)
            y_max_loc = np.max(data, axis=0)
            xticklabels = []
            if hue is not None:
                # for i in df[x].unique().tolist():
                #     for j in df[hue].unique().tolist():
                #         xticklabels.append(i + "-" + j)
                for i in df[x].unique().tolist():
                    xticklabels.append(i)
                x_len = len(df[x].unique().tolist())
                hue_len = len(df[hue].unique().tolist())
                xticks = generate_xticks_with_gap(x_len, hue_len)
                xticks_x_loc = generate_xticks_x_labels(x_len, hue_len)
                default_x_width = 0.85
                legend_hue = df[hue].unique().tolist()
                default_colors = get_color(hue_len)

                # ! stats info
                stats_param = kwargs.get("stats", False)
                res = pd.DataFrame()  # Initialize an empty DataFrame to store results
                ihue = 1
                for i in df[x].unique().tolist():
                    print(i)  # to indicate which 'x'
                    if hue and stats_param:
                        if isinstance(stats_param, dict):
                            if "factor" in stats_param.keys():
                                res_tmp = FuncMultiCmpt(data=df, dv=y, **stats_param)
                            else:
                                res_tmp = FuncMultiCmpt(
                                    data=df[df[x] == i], dv=y, factor=hue, **stats_param
                                )
                        elif bool(stats_param):
                            res_tmp = FuncMultiCmpt(data=df, dv=y, factor=hue)
                        else:
                            res_tmp = "did not work properly"
                        display_output(res_tmp)
                        xloc_curr = hue_len * (ihue - 1)
                        # add_asterisks(ax,res_tmp,xticks[xloc_curr:xloc_curr+hue_len],legend_hue)
                        # res_tmp = [{"x": i, **res_tmp}]
                        # print("here")
                        # df_=pd.DataFrame([res_tmp])
                        # display(df_['pval'][0].tolist()[0])
                        res = pd.concat(
                            [res, pd.DataFrame([res_tmp])], ignore_index=True
                        )
                    ihue += 1
                display_output(res)

            else:
                # ! stats info
                stats_param = kwargs.get("stats", False)
                for i in df[x].unique().tolist():
                    xticklabels.append(i)
                xticks = np.arange(1, len(xticklabels) + 1).tolist()
                xticks_x_loc = np.arange(1, len(xticklabels) + 1).tolist()
                legend_hue = xticklabels
                default_colors = get_color(len(xticklabels))
                default_x_width = 0.5
                res = None
                if x and stats_param:
                    if isinstance(stats_param, dict):
                        if len(xticklabels) > 2:
                            res = FuncMultiCmpt(data=df, dv=y, factor=x, **stats_param)
                        else:
                            res = FuncCmpt(
                                x1=df.loc[df[x] == xticklabels[0], y].tolist(),
                                x2=df.loc[df[x] == xticklabels[1], y].tolist(),
                                **stats_param,
                            )
                    elif bool(stats_param):
                        if len(xticklabels) > 2:
                            res = FuncMultiCmpt(data=df, dv=y, factor=x)
                        else:
                            res = FuncCmpt(
                                x1=df.loc[df[x] == xticklabels[0], y].tolist(),
                                x2=df.loc[df[x] == xticklabels[1], y].tolist(),
                            )
                    else:
                        res = "did not work properly"
                display(res)
                display_output(res)

            # when the xticklabels are too long, rotate the labels a bit
            xangle = 30 if max([len(i) for i in xticklabels]) > 50 else 0
            if kw_figsets is not None:
                kw_figsets = {
                    "ylabel": y,
                    # "xlabel": x,
                    "xticks": xticks_x_loc,  # xticks,
                    "xticklabels": xticklabels,
                    "xangle": xangle,
                    **kw_figsets,
                }
            else:
                kw_figsets = {
                    "ylabel": y,
                    # "xlabel": x,
                    "xticks": xticks_x_loc,  # xticks,
                    "xticklabels": xticklabels,
                    "xangle": xangle,
                }
        else:
            if isinstance(data, np.ndarray):
                df = array2df(data)
                x = "group"
                y = "value"
            xticklabels = []
            stats_param = kwargs.get("stats", False)
            for i in df[x].unique().tolist():
                xticklabels.append(i)
            xticks = np.arange(1, len(xticklabels) + 1).tolist()
            xticks_x_loc = np.arange(1, len(xticklabels) + 1).tolist()
            legend_hue = xticklabels
            default_colors = get_color(len(xticklabels))
            default_x_width = 0.5
            res = None
            if x and stats_param:
                if isinstance(stats_param, dict):
                    res = FuncMultiCmpt(data=df, dv=y, factor=x, **stats_param)
                elif bool(stats_param):
                    res = FuncMultiCmpt(data=df, dv=y, factor=x)
                else:
                    res = "did not work properly"
            display_output(res)
            # xticks = np.arange(1, data.shape[1] + 1).tolist()
            # default_x_width = 0.5
            # default_colors = get_color(len(xticks))
            # legend_hue = None
            # xangle = 0

        # full_order
        opt = kwargs.get("opt", {})

        # load style:
        style_use = None
        for k, v in kwargs.items():
            if "style" in k and "exp" not in k:
                style_use = v
                break
        if style_use:
            try:
                dir_curr_script = os.path.dirname(os.path.abspath(__file__))
                dir_style = dir_curr_script + "/data/styles/"
                style_load = fload(dir_style + style_use + ".json")
                style_load = remove_colors_in_dict(style_load)
                opt.update(style_load)
            except:
                print(f"cannot find the style'{style_name}'")

        opt.setdefault("c", default_colors)
        # if len(opt["c"]) < data.shape[1]:
        #     additional_colors = plt.cm.winter(
        #         np.linspace(0, 1, data.shape[1] - len(opt["c"]))
        #     )
        #     opt["c"] = np.vstack([opt["c"], additional_colors[:, :3]])

        opt.setdefault("loc", {})
        opt["loc"].setdefault("go", 0)
        opt["loc"].setdefault("xloc", xticks)

        # export setting
        opt.setdefault("style", {})
        opt["style"].setdefault("export", None)
        print(opt["style"])

        # opt.setdefault('layer', {})
        opt.setdefault("layer", ["b", "bx", "e", "v", "s", "l"])

        opt.setdefault("b", {})
        opt["b"].setdefault("go", 1)
        opt["b"].setdefault("loc", "c")
        opt["b"].setdefault("FaceColor", opt["c"])
        opt["b"].setdefault("FaceAlpha", 1)
        opt["b"].setdefault("EdgeColor", "k")
        opt["b"].setdefault("EdgeAlpha", 1)
        opt["b"].setdefault("LineStyle", "-")
        opt["b"].setdefault("LineWidth", 0.8)
        opt["b"].setdefault("x_width", default_x_width)
        opt["b"].setdefault("ShowBaseLine", "off")
        opt["b"].setdefault("hatch", None)

        opt.setdefault("e", {})
        opt["e"].setdefault("go", 1)
        opt["e"].setdefault("loc", "l")
        opt["e"].setdefault("LineWidth", 1)
        opt["e"].setdefault("CapLineWidth", 1)
        opt["e"].setdefault("CapSize", 2)
        opt["e"].setdefault("Marker", "none")
        opt["e"].setdefault("LineStyle", "none")
        opt["e"].setdefault("LineColor", "k")
        opt["e"].setdefault("LineJoin", "round")
        opt["e"].setdefault("MarkerSize", "auto")
        opt["e"].setdefault("FaceColor", opt["c"])
        opt["e"].setdefault("MarkerEdgeColor", "none")
        opt["e"].setdefault("Visible", True)
        opt["e"].setdefault("Orientation", "vertical")
        opt["e"].setdefault("error", "sem")
        opt["e"].setdefault("x_width", default_x_width / 5)
        opt["e"].setdefault("cap_dir", "b")

        opt.setdefault("s", {})
        opt["s"].setdefault("go", 1)
        opt["s"].setdefault("loc", "r")
        opt["s"].setdefault("FaceColor", "w")
        opt["s"].setdefault("cmap", None)
        opt["s"].setdefault("FaceAlpha", 1)
        opt["s"].setdefault("x_width", default_x_width / 5)
        opt["s"].setdefault("Marker", "o")
        opt["s"].setdefault("MarkerSize", 15)
        opt["s"].setdefault("LineWidth", 0.8)
        opt["s"].setdefault("MarkerEdgeColor", "k")

        opt.setdefault("l", {})
        opt["l"].setdefault("go", 1)
        opt["l"].setdefault("LineStyle", "-")
        opt["l"].setdefault("LineColor", "k")
        opt["l"].setdefault("LineWidth", 0.5)
        opt["l"].setdefault("LineAlpha", 0.5)

        opt.setdefault("bx", {})
        opt["bx"].setdefault("go", 0)
        opt["bx"].setdefault("loc", "r")
        opt["bx"].setdefault("FaceColor", opt["c"])
        opt["bx"].setdefault("EdgeColor", "k")
        opt["bx"].setdefault("FaceAlpha", 0.85)
        opt["bx"].setdefault("EdgeAlpha", 1)
        opt["bx"].setdefault("LineStyle", "-")
        opt["bx"].setdefault("x_width", default_x_width / 5)
        opt["bx"].setdefault("ShowBaseLine", "off")
        opt["bx"].setdefault("Notch", False)
        opt["bx"].setdefault("Outliers", "on")
        opt["bx"].setdefault("OutlierMarker", "+")
        opt["bx"].setdefault("OutlierColor", "r")
        opt["bx"].setdefault("OutlierSize", 6)
        # opt['bx'].setdefault('PlotStyle', 'traditional')
        # opt['bx'].setdefault('FactorDirection', 'auto')
        opt["bx"].setdefault("LineWidth", 0.5)
        opt["bx"].setdefault("Whisker", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("Orientation", "vertical")
        opt["bx"].setdefault("BoxLineWidth", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("FaceColor", "k")
        opt["bx"].setdefault("WhiskerLineStyle", "-")
        opt["bx"].setdefault("WhiskerLineColor", "k")
        opt["bx"].setdefault("WhiskerLineWidth", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("Caps", True)
        opt["bx"].setdefault("CapLineColor", "k")
        opt["bx"].setdefault("CapLineWidth", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("CapSize", 0.2)
        opt["bx"].setdefault("MedianLine", True)
        opt["bx"].setdefault("MedianLineStyle", "-")
        opt["bx"].setdefault("MedianStyle", "line")
        opt["bx"].setdefault("MedianLineColor", "k")
        opt["bx"].setdefault("MedianLineWidth", opt["bx"]["LineWidth"] * 4)
        opt["bx"].setdefault("MedianLineTop", False)
        opt["bx"].setdefault("MeanLine", False)
        opt["bx"].setdefault("showmeans", opt["bx"]["MeanLine"])
        opt["bx"].setdefault("MeanLineStyle", "-")
        opt["bx"].setdefault("MeanLineColor", "w")
        opt["bx"].setdefault("MeanLineWidth", opt["bx"]["LineWidth"] * 4)

        # Violin plot options
        opt.setdefault("v", {})
        opt["v"].setdefault("go", 0)
        opt["v"].setdefault("x_width", 0.3)
        opt["v"].setdefault("loc", "r")
        opt["v"].setdefault("EdgeColor", "none")
        opt["v"].setdefault("FaceColor", opt["c"])
        opt["v"].setdefault("FaceAlpha", 0.3)
        opt["v"].setdefault("BandWidth", "scott")
        opt["v"].setdefault("Function", "pdf")
        opt["v"].setdefault("Kernel", "gau")
        opt["v"].setdefault("NumPoints", 500)
        opt["v"].setdefault("BoundaryCorrection", "reflection")

        data_m = np.nanmean(data, axis=0)
        nr, nc = data.shape

        for key in kwargs.keys():
            if key in opt:
                if isinstance(kwargs[key], dict):
                    opt[key].update(kwargs[key])
                else:
                    opt[key] = kwargs[key]
        if isinstance(opt["loc"]["xloc"], list):
            xloc = np.array(opt["loc"]["xloc"])
        else:
            xloc = opt["loc"]["xloc"]
        layers = sort_catplot_layers(opt["layer"])

        label_which = kwargs.get("label_which", "barplot")
        if "b" in label_which:
            legend_which = "b"
        elif "s" in label_which:
            legend_which = "s"
        elif "bx" in label_which:
            legend_which = "bx"
        elif "e" in label_which:
            legend_which = "e"
        elif "v" in label_which:
            legend_which = "v"
        else:
            legend_which = None
        for layer in layers:
            if layer == "b" and opt["b"]["go"]:
                if legend_which == "b":
                    plot_bars(data, data_m, opt["b"], xloc, ax, label=legend_hue)
                else:
                    plot_bars(data, data_m, opt["b"], xloc, ax, label=None)
            elif layer == "e" and opt["e"]["go"]:
                if legend_which == "e":
                    plot_errors(data, data_m, opt["e"], xloc, ax, label=legend_hue)
                else:
                    plot_errors(data, data_m, opt["e"], xloc, ax, label=None)
            elif layer == "s" and opt["s"]["go"]:
                if legend_which == "s":
                    plot_scatter(data, opt["s"], xloc, ax, label=legend_hue)
                else:
                    plot_scatter(data, opt["s"], xloc, ax, label=None)
            elif layer == "bx" and opt["bx"]["go"]:
                if legend_which == "bx":
                    plot_boxplot(data, opt["bx"], xloc, ax, label=legend_hue)
                else:
                    plot_boxplot(data, opt["bx"], xloc, ax, label=None)
            elif layer == "v" and opt["v"]["go"]:
                if legend_which == "v":
                    plot_violin(data, opt["v"], xloc, ax, label=legend_hue)
                else:
                    plot_violin(data, opt["v"], xloc, ax, label=None)
            elif all([layer == "l", opt["l"]["go"], opt["s"]["go"]]):
                plot_lines(data, opt["l"], opt["s"], ax)

        if kw_figsets is not None:
            figsets(ax=ax, **kw_figsets)
        show_legend = kwargs.get("show_legend", True)
        if show_legend:
            ax.legend()
        # ! add asterisks in the plot
        # print("here")
        # print(stats_param,isinstance(data, pd.DataFrame),hue)
        if stats_param:
            if isinstance(data, pd.DataFrame):
                if hue is None:
                    display(res)
                    add_asterisks(ax, res, xticks_x_loc, xticklabels)
                else:  # hue is not None
                    ihue = 1
                    for i in df[x].unique().tolist():
                        if stats_param:
                            if isinstance(stats_param, dict):
                                if "factor" in stats_param.keys():
                                    res_tmp = FuncMultiCmpt(
                                        data=df, dv=y, **stats_param
                                    )
                                else:
                                    res_tmp = FuncMultiCmpt(
                                        data=df[df[x] == i],
                                        dv=y,
                                        factor=hue,
                                        **stats_param,
                                    )
                            elif bool(stats_param):
                                res_tmp = FuncMultiCmpt(data=df, dv=y, factor=hue)
                            else:
                                res_tmp = "did not work properly"
                            xloc_curr = hue_len * (ihue - 1)

                            add_asterisks(
                                ax,
                                res_tmp,
                                xticks[xloc_curr : xloc_curr + hue_len],
                                legend_hue,
                            )
                        ihue += 1
            else:
                if len(xticklabels) == 2:
                    tab_res = pd.DataFrame(res[1], index=[0])
                    x1 = df.loc[df[x] == xticklabels[0], y].tolist()
                    x2 = df.loc[df[x] == xticklabels[1], y].tolist()
                    tab_res[f"{xticklabels[0]}(mean±sem)"] = [str_mean_sem(x1)]
                    tab_res[f"{xticklabels[1]}(mean±sem)"] = [str_mean_sem(x2)]

                    display(
                        tab_res,
                        str_mean_sem(df.loc[df[x] == xticklabels[0], y].tolist()),
                    )
                    add_asterisks(
                        ax, res[1], xticks_x_loc, xticklabels, y_loc=np.max([x1, x2])
                    )
                else:
                    add_asterisks(ax, res, xticks_x_loc, xticklabels, yloc=np.max(data))
        style_export = kwargs.get("style_export", None)
        if style_export and (style_export != style_use):
            dir_curr_script = os.path.dirname(os.path.abspath(__file__))
            dir_style = dir_curr_script + "/data/styles/"
            fsave(dir_style + style_export + ".json", opt)

        return ax, opt
    else:
        col_names = data[col].unique().tolist()
        nrow, ncol = kwargs.get("subplots", [len(col_names), 1])
        figsize = kwargs.get("figsize", [3 * ncol, 3 * nrow])
        fig, axs = plt.subplots(nrow, ncol, figsize=figsize, squeeze=False)
        axs = axs.flatten()
        key2rm = ["data", "ax", "col", "subplots"]
        for k2rm in key2rm:
            if k2rm in kwargs:
                del kwargs[k2rm]
        for i, ax in enumerate(axs):
            # ax = axs[i][0] if len(col_names) > 1 else axs[0]
            if i < len(col_names):
                df_sub = data.loc[data[col] == col_names[i]]
                _, opt = catplot(ax=ax, data=df_sub, **kwargs)
                ax.set_title(f"{col}={col_names[i]}")
                x_label = kwargs.get("x", None)
                if x_label:
                    ax.set_xlabel(x_label)
        print(f"Axis layout shape: {axs.shape}")
        return axs, opt


def get_cmap():
    return plt.colormaps()


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


def figsets(*args, **kwargs):
    """
    usage:
        figsets(ax=axs[1],
            ylim=[0, 10],
            spine=2,
            xticklabel=['wake','sleep'],
            yticksdddd=np.arange(0,316,60),
            labels_loc=['right','top'],
            ticks=dict(
            ax='x',
            which='minor',
            direction='out',
            width=2,
            length=2,
            c_tick='m',
            pad=5,
            label_size=11),
            grid=dict(which='minor',
                    ax='x',
                    alpha=.4,
                    c='b',
                    ls='-.',
                    lw=0.75,
                    ),
            supertitleddddd=f'sleep druations\n(min)',
            c_spine='r',
            minor_ticks='xy',
            style='paper',
            box=['right','bottom'],
            xrot=-45,
            yangle=20,
            font_sz = 12,
            legend=dict(labels=['group_a','group_b'],
                        loc='upper left',
                        edgecolor='k',
                        facecolor='r',
                        title='title',
                        fancybox=1,
                        shadow=1,
                        ncols=4,
                        bbox_to_anchor=[-0.5,0.7],
                        alignment='left')
        )
    """
    fig = plt.gcf()
    fontsize = 11
    fontname = "Arial"
    sns_themes = ["white", "whitegrid", "dark", "darkgrid", "ticks"]
    sns_contexts = ["notebook", "talk", "poster"]  # now available "paper"
    scienceplots_styles = [
        "science",
        "nature",
        "scatter",
        "ieee",
        "no-latex",
        "std-colors",
        "high-vis",
        "bright",
        "dark_background",
        "science",
        "high-vis",
        "vibrant",
        "muted",
        "retro",
        "grid",
        "high-contrast",
        "light",
        "cjk-tc-font",
        "cjk-kr-font",
    ]

    def set_step_1(ax, key, value):
        if ("fo" in key) and (("size" in key) or ("sz" in key)):
            fontsize = value
            print(fontsize)
            plt.rcParams.update({"font.size": fontsize})
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
                    if "l" in i.lower() and not "g" in i.lower():
                        ax.yaxis.set_label_position("left")
                    if "r" in i.lower() and not "o" in i.lower():
                        ax.yaxis.set_label_position("right")
                    if "t" in i.lower() and not "l" in i.lower():
                        ax.xaxis.set_label_position("top")
                    if "b" in i.lower() and not "o" in i.lower():
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
        if key == "xlabel" and isinstance(value, dict):
            ax.set_xlabel(**value)
        if key == "ylabel" and isinstance(value, dict):
            ax.set_ylabel(**value)
        # tick location
        if "tic" in key.lower() or "tk" in key.lower():
            if ("loc" in key.lower()) or ("po" in key.lower()):
                if isinstance(value, str):
                    value = [value]
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
                        if i.lower() in ["xnone", "xoff", "none"]:
                            ax.xaxis.set_ticks_position("none")
                        if i.lower() in ["ynone", "yoff", "none"]:
                            ax.yaxis.set_ticks_position("none")
            # ticks / labels
            elif "x" in key.lower():
                if value is None:
                    value = []
                if "la" not in key.lower():
                    ax.set_xticks(value)
                if "la" in key.lower():
                    ax.set_xticklabels(value)
            elif "y" in key.lower():
                if value is None:
                    value = []
                if "la" not in key.lower():
                    ax.set_yticks(value)
                if "la" in key.lower():
                    ax.set_yticklabels(value)
            elif "z" in key.lower():
                if value is None:
                    value = []
                if "la" not in key.lower():
                    ax.set_zticks(value)
                if "la" in key.lower():
                    ax.set_zticklabels(value)
        # rotation
        if "angle" in key.lower() or ("rot" in key.lower()):
            if "x" in key.lower():
                if value in [0, 90, 180, 270]:
                    ax.tick_params(axis="x", rotation=value)
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("center")
                elif value > 0:
                    ax.tick_params(axis="x", rotation=value)
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("right")
                elif value < 0:
                    ax.tick_params(axis="x", rotation=value)
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("left")
            if "y" in key.lower():
                ax.tick_params(axis="y", rotation=value)
                for tick in ax.get_yticklabels():
                    tick.set_horizontalalignment("right")

        if "bo" in key in key:  # box setting, and ("p" in key or "l" in key):
            if isinstance(value, (str, list)):
                locations = []
                for i in value:
                    if "l" in i.lower() and not "t" in i.lower():
                        locations.append("left")
                    if "r" in i.lower() and not "o" in i.lower():  # right
                        locations.append("right")
                    if "t" in i.lower() and not "r" in i.lower():  # top
                        locations.append("top")
                    if "b" in i.lower() and not "t" in i.lower():
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
        if "tick" in key.lower():  # tick ticks tick_para ={}
            if isinstance(value, dict):
                for k, val in value.items():
                    if "wh" in k.lower():
                        ax.tick_params(
                            which=val
                        )  # {'major', 'minor', 'both'}, default: 'major'
                    elif "dir" in k.lower():
                        ax.tick_params(direction=val)  # {'in', 'out', 'inout'}
                    elif "len" in k.lower():  # length
                        ax.tick_params(length=val)
                    elif ("wid" in k.lower()) or ("wd" in k.lower()):  # width
                        ax.tick_params(width=val)
                    elif "ax" in k.lower():  # ax
                        ax.tick_params(axis=val)  # {'x', 'y', 'both'}, default: 'both'
                    elif ("c" in k.lower()) and ("ect" not in k.lower()):
                        ax.tick_params(colors=val)  # Tick color.
                    elif "pad" in k.lower() or "space" in k.lower():
                        ax.tick_params(
                            pad=val
                        )  # float, distance in points between tick and label
                    elif (
                        ("lab" in k.lower() or "text" in k.lower())
                        and ("s" in k.lower())
                        and ("z" in k.lower())
                    ):  # label_size
                        ax.tick_params(
                            labelsize=val
                        )  # float, distance in points between tick and label

        if "mi" in key.lower() and "tic" in key.lower():  # minor_ticks
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

    def set_step_2(ax, key, value):
        if key == "figsize":
            pass
        if "xlim" in key.lower():
            ax.set_xlim(value)
        if "ylim" in key.lower():
            ax.set_ylim(value)
        if "zlim" in key.lower():
            ax.set_zlim(value)
        if "sc" in key.lower():  # scale
            if "x" in key.lower():
                ax.set_xscale(value)
            if "y" in key.lower():
                ax.set_yscale(value)
            if "z" in key.lower():
                ax.set_zscale(value)
        if key == "grid":
            if isinstance(value, dict):
                for k, val in value.items():
                    if "wh" in k.lower():  # which
                        ax.grid(
                            which=val
                        )  # {'major', 'minor', 'both'}, default: 'major'
                    elif "ax" in k.lower():  # ax
                        ax.grid(axis=val)  # {'x', 'y', 'both'}, default: 'both'
                    elif ("c" in k.lower()) and ("ect" not in k.lower()):  # c: color
                        ax.grid(color=val)  # Tick color.
                    elif "l" in k.lower() and ("s" in k.lower()):  # ls:line stype
                        ax.grid(linestyle=val)
                    elif "l" in k.lower() and ("w" in k.lower()):  # lw: line width
                        ax.grid(linewidth=val)
                    elif "al" in k.lower():  # alpha:
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
        if key.lower() in ["spine", "adjust", "ad", "sp", "spi", "adj", "spines"]:
            if isinstance(value, bool) or (value in ["go", "do", "ja", "yes"]):
                if value:
                    adjust_spines(ax)  # dafault distance=2
            if isinstance(value, (float, int)):
                adjust_spines(ax=ax, distance=value)
        if "c" in key.lower() and (
            "sp" in key.lower() or "ax" in key.lower()
        ):  # spine color
            for loc, spi in ax.spines.items():
                spi.set_color(value)
        if "leg" in key.lower():  # legend
            legend_kws = kwargs.get("legend", None)
            if legend_kws:
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
                ax.legend(**legend_kws)
            else:
                ax.legend().remove()

    for arg in args:
        if isinstance(arg, matplotlib.axes._axes.Axes):
            ax = arg
            args = args[1:]
    ax = kwargs.get("ax", plt.gca())
    if "ax" not in locals() or ax is None:
        ax = plt.gca()
    for key, value in kwargs.items():
        set_step_1(ax, key, value)
        set_step_2(ax, key, value)
    for arg in args:
        if isinstance(arg, dict):
            for k, val in arg.items():
                set_step_1(ax, k, val)
            for k, val in arg.items():
                set_step_2(ax, k, val)
        else:
            Nargin = len(args) // 2
            ax.labelFontSizeMultiplier = 1
            ax.titleFontSizeMultiplier = 1
            ax.set_facecolor("w")

            for ip in range(Nargin):
                key = args[ip * 2].lower()
                value = args[ip * 2 + 1]
                set_step_1(ax, key, value)
            for ip in range(Nargin):
                key = args[ip * 2].lower()
                value = args[ip * 2 + 1]
                set_step_2(ax, key, value)
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


from cycler import cycler


def get_color(
    n: int = 1,
    cmap: str = "auto",
    by: str = "start",
    alpha: float = 1.0,
    output: str = "hue",
):
    def cmap2hex(cmap_name):
        cmap_ = matplotlib.pyplot.get_cmap(cmap_name)
        colors = [cmap_(i) for i in range(cmap_.N)]
        return [matplotlib.colors.rgb2hex(color) for color in colors]
        # usage: clist = cmap2hex("viridis")

    # Cycle times, total number is n (default n=10)
    def cycle2list(colorlist, n=10):
        cycler_ = cycler(tmp=colorlist)
        clist = []
        for i, c_ in zip(range(n), cycler_()):
            clist.append(c_["tmp"])
            if i > n:
                break
        return clist

    # Converts hexadecimal color codes to RGBA values
    def hue2rgb(hex_colors, alpha=1.0):
        def hex_to_rgba(hex_color, alpha=1.0):
            """Converts a hexadecimal color code to RGBA values."""
            if hex_color.startswith("#"):
                hex_color = hex_color.lstrip("#")
            rgb = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
            return rgb + (alpha,)

        if isinstance(hex_colors, str):
            return hex_to_rgba(hex_colors, alpha)
        elif isinstance(hex_colors, list):
            """Converts a list of hexadecimal color codes to a list of RGBA values."""
            rgba_values = [hex_to_rgba(hex_color, alpha) for hex_color in hex_colors]
            return rgba_values

    def rgba2hue(rgba_color):
        if len(rgba_color) == 3:
            r, g, b = rgba_color
            a = 1
        else:
            r, g, b, a = rgba_color
        # Convert each component to a scale of 0-255
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        a = int(a * 255)
        if a < 255:
            return "#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, a)
        else:
            return "#{:02X}{:02X}{:02X}".format(r, g, b)

    # Determine color list based on cmap parameter
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

    # Determine method for generating color list
    if "st" in by.lower() or "be" in by.lower():
        clist = cycle2list(colorlist, n=n)
    if "l" in by.lower() or "p" in by.lower():
        clist = []
        [
            clist.append(colorlist[i])
            for i in [int(i) for i in np.linspace(0, len(colorlist) - 1, n)]
        ]

    if "rgb" in output.lower():
        return hue2rgb(clist, alpha)
    elif "h" in output.lower():
        hue_list = []
        [hue_list.append(rgba2hue(i)) for i in hue2rgb(clist, alpha)]
        return hue_list
    else:
        raise ValueError("Invalid output type. Choose 'rgb' or 'hue'.")

    # # Example usage
    # colors = get_color(n=5, cmap="viridis", by="linear", alpha=0.5,output='rgb')
    # print(colors)


""" 
    # n = 7
    # clist = get_color(n, cmap="auto", by="linspace")  # get_color(100)
    # plt.figure(figsize=[8, 5], dpi=100)
    # x = np.linspace(0, 2 * np.pi, 50) * 100
    # y = np.sin(x)
    # for i in range(1, n + 1):
    #     plt.plot(x, y + i, c=clist[i - 1], lw=5, label=str(i))
    # plt.legend()
    # plt.ylim(-2, 20)
    # figsets(plt.gca(), {"style": "whitegrid"}) """


from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt


def stdshade(ax=None, *args, **kwargs):
    # Separate kws_line and kws_fill if necessary
    kws_line = kwargs.pop("kws_line", {})
    kws_fill = kwargs.pop("kws_fill", {})

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
                    acolor = hue2rgb(args[iarg])
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
    smth = kwargs.get("smth", smth)
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
            wings = savgol_filter(
                np.nanstd(y, axis=0, ddof=1) / np.sqrt(y.shape[0]), smth, 1
            )
        else:
            wings = np.nanstd(y, axis=0, ddof=1) / np.sqrt(y.shape[0])
    elif paraStdSem == "std":
        if smth > 1:
            wings = savgol_filter(np.nanstd(y, axis=0, ddof=1), smth, 1)
        else:
            wings = np.nanstd(y, axis=0, ddof=1)

    # fill_kws = kwargs.get('fill_kws', {})
    # line_kws = kwargs.get('line_kws', {})

    # setting form kwargs
    lw = kwargs.get("lw", 0.5)
    ls = kwargs.get("ls", plotStyle)
    marker = kwargs.get("marker", plotMarker)
    label = kwargs.get("label", None)
    label_line = kwargs.get("label_line", None)
    label_fill = kwargs.get("label_fill", None)
    alpha = kwargs.get("alpha", alpha)
    color = kwargs.get("color", acolor)
    if not label_line and label:
        label_line = label
    kwargs["lw"] = lw
    kwargs["ls"] = ls
    kwargs["label_line"] = label_line
    kwargs["label_fill"] = label_fill

    # set kws_line
    if "color" not in kws_line:
        kws_line["color"] = color
    if "lw" not in kws_line:
        kws_line["lw"] = lw
    if "ls" not in kws_line:
        kws_line["ls"] = ls
    if "marker" not in kws_line:
        kws_line["marker"] = marker
    if "label" not in kws_line:
        kws_line["label"] = label_line

    # set kws_line
    if "color" not in kws_fill:
        kws_fill["color"] = color
    if "alpha" not in kws_fill:
        kws_fill["alpha"] = alpha
    if "lw" not in kws_fill:
        kws_fill["lw"] = 0
    if "label" not in kws_fill:
        kws_fill["label"] = label_fill

    fill = ax.fill_between(x, yMean + wings, yMean - wings, **kws_fill)
    line = ax.plot(x, yMean, **kws_line)

    # figsets
    kw_figsets = kwargs.get("figsets", None)
    if kw_figsets is not None:
        figsets(ax=ax, **kw_figsets)

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


def adjust_spines(ax=None, spines=["left", "bottom"], distance=2):
    if ax is None:
        ax = plt.gca()
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(("outward", distance))  # outward by 2 points
            # spine.set_smart_bounds(True)
        else:
            spine.set_color("none")  # don't draw spine
    # turn off ticks where there is no spine
    if "left" in spines:
        ax.yaxis.set_ticks_position("left")
    else:
        ax.yaxis.set_ticks([])
    if "bottom" in spines:
        ax.xaxis.set_ticks_position("bottom")
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])


# And then plot the data:


def add_colorbar(im, width=None, pad=None, **kwargs):
    # usage: add_colorbar(im, width=0.01, pad=0.005, label="PSD (dB)", shrink=0.8)
    l, b, w, h = im.axes.get_position().bounds  # get boundaries
    width = width or 0.1 * w  # get width of the colorbar
    pad = pad or width  # get pad between im and cbar
    fig = im.axes.figure  # get figure of image
    cax = fig.add_axes([l + w + pad, b, width, h])  # define cbar Axes
    return fig.colorbar(im, cax=cax, **kwargs)  # draw cbar


def generate_xticks_with_gap(x_len, hue_len):
    """
    Generate a concatenated array based on x_len and hue_len,
    and return only the positive numbers.

    Parameters:
    - x_len: int, number of segments to generate
    - hue_len: int, length of each hue

    Returns:
    - numpy array: Concatenated array containing only positive numbers
    """

    arrays = [
        np.arange(1, hue_len + 1) + hue_len * (x_len - i) + (x_len - i)
        for i in range(max(x_len, hue_len), 0, -1)  # i iterates from 3 to 1
    ]
    concatenated_array = np.concatenate(arrays)
    positive_array = concatenated_array[concatenated_array > 0].tolist()

    return positive_array


def generate_xticks_x_labels(x_len, hue_len):
    arrays = [
        np.arange(1, hue_len + 1) + hue_len * (x_len - i) + (x_len - i)
        for i in range(max(x_len, hue_len), 0, -1)  # i iterates from 3 to 1
    ]
    return [np.mean(i) for i in arrays if np.mean(i) > 0]


def remove_colors_in_dict(
    data: dict, sections_to_remove_facecolor=["b", "e", "s", "bx", "v"]
):
    # Remove "FaceColor" from specified sections
    for section in sections_to_remove_facecolor:
        if section in data and ("FaceColor" in data[section]):
            del data[section]["FaceColor"]

    if "c" in data:
        del data["c"]
    if "loc" in data:
        del data["loc"]
    return data


def add_asterisks(ax, res, xticks_x_loc, xticklabels, **kwargs_funcstars):
    y_max_loc = kwargs_funcstars.get("kwargs_funcstars", None)
    if len(xticklabels) > 2:
        if isinstance(res, dict):
            display(res["res_tab"])
            pval_groups = res["res_tab"]["p-unc"].tolist()[0]
        else:
            pval_groups = res["res_tab"]["PR(>F)"].tolist()[0]
        # print(f"p=:{pval_groups}")
        # print(f"xticks:{xticks}")
        # print(f"xticks_x_loc:{xticks_x_loc}")
        if pval_groups <= 0.05:
            A_list = res["res_posthoc"]["A"].tolist()
            B_list = res["res_posthoc"]["B"].tolist()
            xticklabels_array = np.array(xticklabels)
            yscal_ = 0.99
            for A, B, P in zip(
                res["res_posthoc"]["A"].tolist(),
                res["res_posthoc"]["B"].tolist(),
                res["res_posthoc"]["p-unc"].tolist(),
            ):
                index_A = np.where(xticklabels_array == A)[0][0]
                index_B = np.where(xticklabels_array == B)[0][0]
                print(index_A, A, index_B, B, P)
                FuncStars(
                    ax=ax,
                    x1=xticks_x_loc[index_A],
                    x2=xticks_x_loc[index_B],
                    pval=P,
                    yscale=yscal_,
                    **kwargs_funcstars,
                )
                if P <= 0.05:
                    yscal_ -= 0.1
    else:
        pval_groups = res["pval"]
        FuncStars(
            ax=ax,
            x1=1,
            x2=2,
            pval=pval_groups,
            **kwargs_funcstars,
        )
