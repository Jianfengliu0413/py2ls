from scipy.ndimage import convolve1d
from scipy.signal import savgol_filter
import pingouin as pg
from scipy import stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)


# FuncStars --v 0.1.1
def FuncStars(
    ax=None,
    pval=None,
    ylim=None,
    xlim=None,
    symbol="*",
    yscale=0.95,
    y_loc=None,
    x1=0,
    x2=1,
    alpha=0.05,
    fontsize=14,
    fontsize_note=12,
    rotation=0,
    fontname="Arial",
    values_below=None,
    linego=True,
    linestyle="-",
    linecolor="k",
    linewidth=0.8,
    nsshow="off",
    symbolcolor="k",
    tailindicator=[0.05, 0.05],
    report=None,
    report_scale=-0.1,
    report_loc=None,
    **kwargs
):
    if ax is None:
        ax = plt.gca()
    if ylim is None:
        ylim = ax.get_ylim()
    if xlim is None:
        xlim = ax.get_xlim()
    if report_loc is None and report is not None:
        report_loc = np.min(ylim) + report_scale * np.abs(np.diff(ylim))
    if report_scale > 0:
        report_scale = -np.abs(report_scale)
    yscale = np.float64(yscale)
    if y_loc is None:
        y_loc = np.min(ylim) + yscale * (np.max(ylim) - np.min(ylim))
    else:
        y_loc=y_loc+(1-yscale) * np.abs(np.diff(ylim))+0.1 *y_loc
    xcenter = np.mean([x1, x2])
    if pval is not None:
        # ns / *
        if alpha < pval:
            if nsshow == "on":
                ns_str = f"p={round(pval, 3)}" if pval < 0.9 else "ns"
                color = "m" if pval < 0.1 else "k"
                ax.text(
                    xcenter,
                    y_loc,
                    ns_str,
                    ha="center",
                    va="bottom",  # 'center_baseline',
                    fontsize=fontsize - 6 if fontsize > 6 else fontsize,
                    fontname=fontname,
                    color=color,
                    rotation=rotation,
                    # bbox=dict(facecolor=None, edgecolor=None, color=None, linewidth=None)
                )
        elif 0.01 < pval <= alpha:
            ax.text(
                xcenter,
                y_loc,
                symbol,
                ha="center",
                va="top",#"center_baseline",
                fontsize=fontsize,
                fontname=fontname,
                color=symbolcolor,
            )
        elif 0.001 < pval <= 0.01:
            ax.text(
                xcenter,
                y_loc,
                symbol * 2,
                ha="center",
                va="top",#"center_baseline",
                fontsize=fontsize,
                fontname=fontname,
                color=symbolcolor,
            )
        elif 0 < pval <= 0.001:
            ax.text(
                xcenter,
                y_loc,
                symbol * 3,
                ha="center",
                va="top",#"center_baseline",
                fontsize=fontsize,
                fontname=fontname,
                color=symbolcolor,
            )
        # lines indicators
        if linego and 0 < pval <= 0.05:
            # horizontal line
            if yscale <= 0.99:
                ax.plot(
                    [x1 + np.abs(np.diff(xlim)) * 0.01, x2 - np.abs(np.diff(xlim)) * 0.01],
                    [
                        y_loc - np.abs(np.diff(ylim)) * 0.03,
                        y_loc - np.abs(np.diff(ylim)) * 0.03,
                    ],
                    linestyle=linestyle,
                    color=linecolor,
                    linewidth=linewidth,
                )
                # vertical line
                ax.plot(
                    [x1 + np.abs(np.diff(xlim)) * 0.01, x1 + np.abs(np.diff(xlim)) * 0.01],
                    [
                        y_loc - np.abs(np.diff(ylim)) * tailindicator[0],
                        y_loc - np.abs(np.diff(ylim)) * 0.03,
                    ],
                    linestyle=linestyle,
                    color=linecolor,
                    linewidth=linewidth,
                )
                ax.plot(
                    [x2 - np.abs(np.diff(xlim)) * 0.01, x2 - np.abs(np.diff(xlim)) * 0.01],
                    [
                        y_loc - np.abs(np.diff(ylim)) * tailindicator[1],
                        y_loc - np.abs(np.diff(ylim)) * 0.03,
                    ],
                    linestyle=linestyle,
                    color=linecolor,
                    linewidth=linewidth,
                )
            else:
                ax.plot(
                    [x1 + np.abs(np.diff(xlim)) * 0.01, x2 - np.abs(np.diff(xlim)) * 0.01],
                    [
                        np.min(ylim)
                        + 0.95 * (np.max(ylim) - np.min(ylim))
                        - np.abs(np.diff(ylim)) * 0.002,
                        np.min(ylim)
                        + 0.95 * (np.max(ylim) - np.min(ylim))
                        - np.abs(np.diff(ylim)) * 0.002,
                    ],
                    linestyle=linestyle,
                    color=linecolor,
                    linewidth=linewidth,
                )
                # vertical line
                ax.plot(
                    [x1 + np.abs(np.diff(xlim)) * 0.01, x1 + np.abs(np.diff(xlim)) * 0.01],
                    [
                        np.min(ylim)
                        + 0.95 * (np.max(ylim) - np.min(ylim))
                        - np.abs(np.diff(ylim)) * tailindicator[0],
                        np.min(ylim)
                        + 0.95 * (np.max(ylim) - np.min(ylim))
                        - np.abs(np.diff(ylim)) * 0.002,
                    ],
                    linestyle=linestyle,
                    color=linecolor,
                    linewidth=linewidth,
                )
                ax.plot(
                    [x2 - np.abs(np.diff(xlim)) * 0.01, x2 - np.abs(np.diff(xlim)) * 0.01],
                    [
                        np.min(ylim)
                        + 0.95 * (np.max(ylim) - np.min(ylim))
                        - np.abs(np.diff(ylim)) * tailindicator[1],
                        np.min(ylim)
                        + 0.95 * (np.max(ylim) - np.min(ylim))
                        - np.abs(np.diff(ylim)) * 0.002,
                    ],
                    linestyle=linestyle,
                    color=linecolor,
                    linewidth=linewidth,
                )
    if values_below is not None:
        ax.text(
            xcenter,
            y_loc * (-0.1),
            values_below,
            ha="center",
            va="bottom",  # 'center_baseline', rotation=rotation,
            fontsize=fontsize_note,
            fontname=fontname,
            color="k",
        )
    # report / comments
    if report is not None:
        ax.text(
            xcenter,
            report_loc,
            report,
            ha="left",
            va="bottom",  # 'center_baseline', rotation=rotation,
            fontsize=fontsize_note,
            fontname=fontname,
            color=".7",
        )


def FuncCmpt(x1, x2, pmc="auto", pair="unpaired", verbose=True):
    # output = {}

    # pmc correction: 'parametric'/'non-parametric'/'auto'
    # meawhile get the opposite setting (to compare the results)
    # def corr_pmc(pmc):
    #     cfg_pmc = None
    #     if pmc.lower() in {"pmc", "parametric"} and pmc.lower() not in {
    #         "npmc",
    #         "nonparametric",
    #         "non-parametric",
    #     }:
    #         cfg_pmc = "parametric"
    #     elif pmc.lower() in {
    #         "npmc",
    #         "nonparametric",
    #         "non-parametric",
    #     } and pmc.lower() not in {"pmc", "parametric"}:
    #         cfg_pmc = "non-parametric"
    #     else:
    #         cfg_pmc = "auto"
    #     return cfg_pmc

    # def corr_pair(pair):
    #     cfg_pair = None
    #     if "pa" in pair.lower() and "np" not in pair.lower():
    #         cfg_pair = "paired"
    #     elif "np" in pair.lower():
    #         cfg_pair = "unpaired"
    #     return cfg_pair

    # def check_normality(data, verbose=True):
    #     stat_shapiro, pval_shapiro = stats.shapiro(data)
    #     if pval_shapiro > 0.05:
    #         Normality = True
    #     else:
    #         Normality = False
    #     if verbose:
    #         (
    #             print(f"\n normally distributed\n")
    #             if Normality
    #             else print(f"\n NOT normally distributed\n")
    #         )
    #     return Normality

    def sub_cmpt_2group(x1, x2, cfg_pmc="pmc", pair="unpaired", verbose=True):
        output = {}
        nX1 = np.sum(~np.isnan(x1))
        nX2 = np.sum(~np.isnan(x2))
        if cfg_pmc == "parametric" or cfg_pmc == "auto":
            # VarType correction by checking variance Type via "levene"
            stat_lev, pval_lev = stats.levene(
                x1, x2, center="median", proportiontocut=0.05
            )
            VarType = True if pval_lev > 0.05 and nX1 == nX2 else False
            # print(pair)
            if "np" in pair:  # 'unpaired'
                if VarType and Normality:
                    # The independent t-test requires that the dependent variable is approximately normally
                    # distributed within each group
                    # Note: Technically, it is the residuals that need to be normally distributed, but for
                    # an independent t-test, both will give you the same result.
                    stat_value, pval = stats.ttest_ind(
                        x1,
                        x2,
                        axis=0,
                        equal_var=True,
                        nan_policy="omit",
                        alternative="two-sided",
                    )
                    notes_stat = "unpaired t test"
                    notes_APA = (
                        f"t({nX1+nX2-2})={round(stat_value,3)},p={round(pval,3)}"
                    )
                else:
                    # If the Levene's Test for Equality of Variances is statistically significant,
                    # which indicates that the group variances are unequal in the population, you
                    # can correct for this violation by not using the pooled estimate for the error
                    # term for the t-statistic, but instead using an adjustment to the degrees of
                    # freedom using the Welch-Satterthwaite method
                    stat_value, pval = stats.ttest_ind(
                        x1,
                        x2,
                        axis=0,
                        equal_var=False,
                        nan_policy="omit",
                        alternative="two-sided",
                    )
                    notes_stat = "Welchs t-test"
                    # note: APA FORMAT
                    notes_APA = (
                        f"t({nX1+nX2-2})={round(stat_value,3)},p={round(pval,3)}"
                    )
            elif "pa" in pair and "np" not in pair:  # 'paired'
                # the paired-samples t-test is considered “robust” in handling violations of normality
                # to some extent. It can still yield valid results even if the data is not normally
                # distributed. Therefore, this test typically requires only approximately normal data
                stat_value, pval = stats.ttest_rel(
                    x1, x2, axis=0, nan_policy="omit", alternative="two-sided"
                )
                notes_stat = "paired t test"
                # note: APA FORMAT
                notes_APA = (
                    f"t({sum([nX1-1])})={round(stat_value,3)},p={round(pval,3)}"
                )
        elif cfg_pmc == "non-parametric":
            if "np" in pair:  # Perform Mann-Whitney
                stat_value, pval = stats.mannwhitneyu(
                    x1, x2, method="exact", nan_policy="omit"
                )
                notes_stat = "Mann-Whitney U"
                if nX1 == nX2:
                    notes_APA = f"U(n={nX1})={round(stat_value,3)},p={round(pval,3)}"
                else:
                    notes_APA = f"U(n1={nX1},n2={nX2})={round(stat_value,3)},p={round(pval,3)}"
            elif "pa" in pair and "np" not in pair:  # Wilcoxon signed-rank test
                stat_value, pval = stats.wilcoxon(
                    x1, x2, method="exact", nan_policy="omit"
                )
                notes_stat = "Wilcoxon signed-rank"
                if nX1 == nX2:
                    notes_APA = f"Z(n={nX1})={round(stat_value,3)},p={round(pval,3)}"
                else:
                    notes_APA = f"Z(n1={nX1},n2={nX2})={round(stat_value,3)},p={round(pval,3)}"

        # filling output
        output["stat"] = stat_value
        output["pval"] = pval
        output["method"] = notes_stat
        output["APA"] = notes_APA
        if verbose:
            print(f"{output['method']}\n {notes_APA}\n\n")

        return output, pval

    Normality1 = check_normality(x1, verbose=verbose)
    Normality2 = check_normality(x2, verbose=verbose)
    Normality = True if all([Normality1, Normality2]) else False

    cfg_pmc = corr_pmc(pmc)
    cfg_pair = corr_pair(pair)

    output, p = sub_cmpt_2group(x1, x2, cfg_pmc=cfg_pmc, pair=cfg_pair, verbose=verbose)
    return p, output


# ======compare 2 group test===================================================
# # Example
# x1 = [19, 22, 16, 29, 24]
# x2 = [20, 11, 17, 12, 22]

# p, res= FuncCmpt(x1, x2, pmc='pmc', pair='unparrr')

# =============================================================================

# =============================================================================
# # method = ['anova',  # 'One-way and N-way ANOVA',
# #           'rm_anova',  # 'One-way and two-way repeated measures ANOVA',
# #           'mixed_anova',  # 'Two way mixed ANOVA',
# #           'welch_anova',  # 'One-way Welch ANOVA',
# #           'kruskal',  # 'Non-parametric one-way ANOVA'
# #           'friedman',  # Non-parametric one-way repeated measures ANOVA
# #           ]
# =============================================================================


# =============================================================================
# # method = ['anova',  # 'One-way and N-way ANOVA',
# #           'rm_anova',  # 'One-way and two-way repeated measures ANOVA',
# #           'mixed_anova',  # 'Two way mixed ANOVA',
# #           'welch_anova',  # 'One-way Welch ANOVA',
# #           'kruskal',  # 'Non-parametric one-way ANOVA'
# #           'friedman',  # Non-parametric one-way repeated measures ANOVA
# #           ]
# =============================================================================


def str_mean_sem(data: list, delimit=3):
    mean_ = np.nanmean(data)
    sem_ = np.nanstd(data, ddof=1) / np.sqrt(sum(~np.isnan(data)))
    return str(round(mean_, delimit)) + "±" + str(round(sem_, delimit))


def FuncMultiCmpt(
    pmc="pmc",
    pair="unpair",
    data=None,
    dv=None,
    factor=None,
    ss_type=2,
    detailed=True,
    effsize="np2",
    correction="auto",
    between=None,
    within=None,
    subject=None,
    group=None,
    verbose=True,
    post_hoc=False
):
    if group is None:
        group = factor

    norm_array = []
    if len(group) > 1:
        pass
    else:
        for sub_group in data[group].unique():
            norm_curr = check_normality(data.loc[data[group] == sub_group, dv])
            norm_array.append(norm_curr)
    norm_all = True if all(norm_array) else False

    # Homogeneity of Variances:
    # Check for homogeneity of variances (homoscedasticity) among groups.
    # Levene's test or Bartlett's test can be used for this purpose.
    # If variances are significantly different, consider transformations or use a
    # robust ANOVA method.

    # # =============================================================================
    # # # method1: stats.levene
    # # =============================================================================
    # # data_array = []
    # # for sub_group in df["group"].unique():
    # #     data_array.append(df.loc[df['group'] == sub_group, 'values'].values)
    # # print(data_array)
    # # variance_all = stats.levene(data_array[0],data_array[1],data_array[2])

    # =============================================================================
    # # method2: pingouin.homoscedasticity
    # =============================================================================
    res_levene = None
    if len(group) > 1:
        pass
    else:
        variance_all = pg.homoscedasticity(
            data, dv=dv, group=group, method="levene", alpha=0.05
        )
        res_levene = True if variance_all.iloc[0, 1] > 0.05 else False
    # =============================================================================
    # # ANOVA Assumptions:
    # # Ensure that the assumptions of independence, homogeneity of variances, and
    # # normality are reasonably met before proceeding.
    # =============================================================================
    notes_norm = "normally" if norm_all else "NOT-normally"
    notes_variance = "equal" if res_levene else "unequal"
    print(f"Data is {notes_norm} distributed, shows {notes_variance} variance")

    cfg_pmc = corr_pmc(pmc)
    cfg_pair = corr_pair(pair)
    output = {}
    if (cfg_pmc == "parametric") or (cfg_pmc == "auto"):
        if "np" in cfg_pair:  # 'unpaired'
            if cfg_pmc == "auto":
                if norm_all:
                    if res_levene:
                        res_tab = run_anova(
                            data,
                            dv,
                            factor,
                            ss_type=ss_type,
                            detailed=True,
                            effsize="np2",
                        )
                        notes_stat = f"{data[factor].nunique()} Way ANOVA"
                        notes_APA = extract_apa(res_tab)

                    else:
                        res_tab = run_welchanova(data, dv, factor)
                        notes_stat = f"{data[factor].nunique()} Way Welch ANOVA"
                        notes_APA = extract_apa(res_tab)
                else:
                    res_tab = run_kruskal(data, dv, factor)
                    notes_stat = (
                        f"Non-parametric Kruskal: {data[factor].nunique()} Way ANOVA"
                    )
                    notes_APA = extract_apa(res_tab)

            elif cfg_pmc == "parametric":
                res_tab = run_anova(
                    data, dv, factor, ss_type=ss_type, detailed=True, effsize="np2"
                )
                notes_stat = f"{data[factor].nunique()} Way ANOVA"
                notes_APA = extract_apa(res_tab)

        elif "pa" in cfg_pair and "np" not in cfg_pair:  # 'paired'
            res_tab = run_rmanova(
                data,
                dv,
                factor,
                subject,
                correction="auto",
                detailed=True,
                effsize="ng2",
            )
            notes_stat = f"{data[factor].nunique()} Way Repeated measures ANOVA"
            notes_APA = extract_apa(res_tab)

        elif "mix" in cfg_pair or "both" in cfg_pair:
            print("mix")
            res_tab = run_mixedanova(data, dv, between, within, subject)
            # notes_stat = f'{len(sum(len(between)+sum(len(within))))} Way Mixed ANOVA'
            notes_stat = ""
            # n_inter = res_tab.loc(res_tab["Source"] == "Interaction")
            # print(n_inter)
            notes_APA = extract_apa(res_tab)

    elif cfg_pmc == "non-parametric":
        if "np" in cfg_pair:  # 'unpaired'
            res_tab = run_kruskal(data, dv, factor)
            notes_stat = f"Non-parametric Kruskal: {data[factor].nunique()} Way ANOVA"
            notes_APA = [f'H({res_tab.ddof1[0]},N={data.shape[0]})={round(res_tab.H[0],3)},p={round(res_tab["p-unc"][0],3)}']

        elif "pa" in cfg_pair and "np" not in cfg_pair:  # 'paired'
            res_tab = run_friedman(data, dv, factor, subject, method="chisq")
            notes_stat = f"Non-parametric {data[factor].nunique()} Way Friedman repeated measures ANOVA"
            notes_APA = [f'X^2({res_tab.ddof1[0]})={round(res_tab.Q[0],3)},p={round(res_tab["p-unc"][0],3)}']

    # =============================================================================
    # # Post-hoc
    # Post-Hoc Tests (if significant):
    # If ANOVA indicates significant differences, perform post-hoc tests (e.g.,
    # Tukey's HSD, Bonferroni, or Scheffé) to identify which groups differ from each other.
    # # https://pingouin-stats.org/build/html/generated/pingouin.pairwise_tests.html
    # =============================================================================
    go_pmc = True if cfg_pmc == "parametric" else False
    go_subject = subject if ("pa" in cfg_pair) and ("np" not in cfg_pair) else None
    go_mix_between = between if ("mix" in cfg_pair) or ("both" in cfg_pair) else None
    go_mix_between = None if ("pa" in cfg_pair) or ("np" not in cfg_pair) else factor
    go_mix_within = within if ("mix" in cfg_pair) or ("both" in cfg_pair) else None
    go_mix_within = factor if ("pa" in cfg_pair) or ("np" not in cfg_pair) else None

    if res_tab["p-unc"][0] <= 0.05:
        post_hoc=True
    if post_hoc:
        # Pairwise Comparisons
        method_post_hoc = [
            "bonf",  # 'bonferroni',  # : one-step correction
            "sidak",  # one-step correction
            "holm",  # step-down method using Bonferroni adjustments
            "fdr_bh",  # Benjamini/Hochberg (non-negative)
            "fdr_by",  # Benjamini/Yekutieli (negative)
        ]
        # *********? not work properly below*********
        # res_posthoc = pd.DataFrame()

        # for met in method_post_hoc:
        #     post_curr = pg.pairwise_tests(
        #         data=data,
        #         dv=dv,
        #         between=go_mix_between,
        #         within=go_mix_within,
        #         subject=go_subject,
        #         parametric=go_pmc,
        #         marginal=True,
        #         alpha=0.05,
        #         alternative="two-sided",
        #         padjust=met,
        #         nan_policy="listwise",#"pairwise"
        #         return_desc=True
        #     )
        #     res_posthoc = pd.concat([res_posthoc, post_curr], ignore_index=True)
        # *********? not work properly above *********

        # add ttest
        data_within = df2array(data=data, x=factor, y=dv)
        colname_within = data[factor].unique().tolist()
        nrow, ncol = data_within.shape
        res_posthoc = pd.DataFrame()
        for icol in range(ncol):
            for icol_ in range(1, ncol):
                if icol_ > icol:
                    res_posthoc_ = pd.DataFrame()
                    _, res__ = FuncCmpt(
                        x1=data_within[:, icol],
                        x2=data_within[:, icol_],
                        pmc=pmc,
                        pair=pair,
                        verbose=False,
                    )
                    res_posthoc_["A"] = pd.Series(colname_within[icol])
                    res_posthoc_["B"] = pd.Series(colname_within[icol_])
                    res_posthoc_["mean(A)"] = pd.Series(
                        str_mean_sem(data_within[:, icol])
                    )
                    res_posthoc_["mean(B)"] = pd.Series(
                        str_mean_sem(data_within[:, icol_])
                    )
                    res_posthoc_["APA"] = pd.Series(res__["APA"])
                    res_posthoc_["p-unc"] = pd.Series(res__["pval"])
                    res_posthoc_["method"] = pd.Series(res__["method"])
                    res_posthoc = pd.concat(
                        [res_posthoc, res_posthoc_], ignore_index=True
                    )
    else:
        res_posthoc = None
    output["res_posthoc"] = res_posthoc
    # =============================================================================
    #     # filling output
    # =============================================================================

    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_colwidth', None)  # No limit on column width
    pd.set_option('display.expand_frame_repr', False)  # Prevent line-wrapping

    output["stat"] = notes_stat
    # print(output['APA'])
    output["APA"] = notes_APA
    output["pval"] = res_tab["p-unc"]
    output["res_tab"] = res_tab
    if res_tab.shape[0] == len(notes_APA):
        output["res_tab"]["APA"] = output["APA"]  # note APA in the table
    return output


def display_output(output: dict):
    if isinstance(output, pd.DataFrame):
        output = output.to_dict(orient="list")
    # ['res_posthoc', 'stat', 'APA', 'pval', 'res_tab'] 

    # ? show APA
    # print(f"\n\ndisplay stat_output")
    # try:
    #     print(f"APA: {output["APA"]}")
    # except:
    #     pass
    try:
        print("stats table:  ⤵")
        display(output["res_tab"])
    except:
        pass
    try:
        print(f"APA  ⤵\n{output["APA"][0]}  ⤵\npost-hoc analysis ⤵")
        display(output["res_posthoc"])
    except:
        pass


def corr_pair(pair):
    cfg_pair = None
    if "pa" in pair.lower() and "np" not in pair.lower():
        cfg_pair = "paired"
    elif "np" in pair.lower():
        cfg_pair = "unpaired"
    elif "mix" in pair.lower():
        cfg_pair = "mix"
    return cfg_pair


def check_normality(data, verbose=True):
    stat_shapiro, pval_shapiro = stats.shapiro(data)
    if pval_shapiro > 0.05:
        Normality = True
    else:
        Normality = False
    if verbose:
        (
            print(f"\n normally distributed\n")
            if Normality
            else print(f"\n NOT normally distributed\n")
        )
    return Normality


def corr_pmc(pmc):
    cfg_pmc = None
    if pmc.lower() in {"pmc", "parametric"} and pmc.lower() not in {
        "upmc",
        "npmc",
        "nonparametric",
        "non-parametric",
    }:
        cfg_pmc = "parametric"
    elif pmc.lower() in {
        "upmc",
        "npmc",
        "nonparametric",
        "non-parametric",
    } and pmc.lower() not in {"pmc", "parametric"}:
        cfg_pmc = "non-parametric"
    elif pmc.lower() in {
        "mix",
        "both",
    }:
        cfg_pmc = "mix"
    else:
        cfg_pmc = "auto"
    return cfg_pmc


def extract_apa(res_tab):
    notes_APA = []
    if "ddof1" in res_tab:
        for irow in range(res_tab.shape[0]):
            note_tmp = f'{res_tab.Source[irow]}:F{round(res_tab.ddof1[irow]),round(res_tab.ddof2[irow])}={round(res_tab.F[irow],3)},p={round(res_tab["p-unc"][irow],3)}'
            notes_APA.append(note_tmp)
    elif "DF" in res_tab: 
        for irow in range(res_tab.shape[0] - 1):
            note_tmp = f'{res_tab.Source[irow]}:F{round(res_tab.DF[irow]),round(res_tab.DF[res_tab.shape[0]-1])}={round(res_tab.F[irow],3)},p={round(res_tab["p-unc"][irow],3)}'
            notes_APA.append(note_tmp)
        notes_APA.append(np.nan)
    elif "DF1" in res_tab:  # in 'mix' case
        for irow in range(res_tab.shape[0]):
            note_tmp = f'{res_tab.Source[irow]}:F{round(res_tab.DF1[irow]),round(res_tab.DF2[irow])}={round(res_tab.F[irow],3)},p={round(res_tab["p-unc"][irow],3)}'
            notes_APA.append(note_tmp)
    return notes_APA


def anovatable(res_tab):
    if "df" in res_tab:  # statsmodels
        res_tab["mean_sq"] = res_tab[:]["sum_sq"] / res_tab[:]["df"]
        res_tab["est_sq"] = res_tab[:-1]["sum_sq"] / sum(res_tab["sum_sq"])
        res_tab["omega_sq"] = (
            res_tab[:-1]["sum_sq"] - (res_tab[:-1]["df"] * res_tab["mean_sq"][-1])
        ) / (sum(res_tab["sum_sq"]) + res_tab["mean_sq"][-1])
    elif "DF" in res_tab:
        res_tab["MS"] = res_tab[:]["SS"] / res_tab[:]["DF"]
        res_tab["est_sq"] = res_tab[:-1]["SS"] / sum(res_tab["SS"])
        res_tab["omega_sq"] = (
            res_tab[:-1]["SS"] - (res_tab[:-1]["DF"] * res_tab["MS"][1])
        ) / (sum(res_tab["SS"]) + res_tab["MS"][1])
    if "p-unc" in res_tab:
        if "np2" in res_tab:
            res_tab["est_sq"] = res_tab["np2"]
        if "p-unc" in res_tab:
            res_tab["PR(>F)"] = res_tab["p-unc"]
    return res_tab


def run_anova(data, dv, factor, ss_type=2, detailed=True, effsize="np2"):
    # perform ANOVA
    # =============================================================================
    # #     # ANOVA (input: formula, dataset)
    # =============================================================================
    #     # note: if the data is balanced (equal sample size for each group), Type 1, 2, and 3 sums of squares
    #     # (typ parameter) will produce similar results.
    #     lm = ols("values ~ C(group)", data=df).fit()
    #     res_tab = anova_lm(lm, typ=ss_type)

    #     # however, it does not provide any effect size measures to tell if the
    #     # statistical significance is meaningful. The function below calculates
    #     # eta-squared () and omega-squared (). A quick note,  is the exact same
    #     # thing as  except when coming from the ANOVA framework people call it ;
    #     # is considered a better measure of effect size since it is unbiased in
    #     # it's calculation by accounting for the degrees of freedom in the model.
    #     # note: No effect sizes are calculated when using statsmodels.
    #     # to calculate eta squared, use the sum of squares from the table
    # res_tab = anovatable(res_tab)

    # =============================================================================
    #     # alternativ for ANOVA
    # =============================================================================
    res_tab = pg.anova(
        dv=dv,
        between=factor,
        data=data,
        detailed=detailed,
        ss_type=ss_type,
        effsize=effsize,
    )
    res_tab = anovatable(res_tab)
    return res_tab


def run_rmanova(
    data, dv, factor, subject, correction="auto", detailed=True, effsize="ng2"
):
    # One-way repeated-measures ANOVA using a long-format dataset.
    res_tab = pg.rm_anova(
        data=data,
        dv=dv,
        within=factor,
        subject=subject,
        detailed=detailed,
        effsize=effsize,
    )
    return res_tab


def run_welchanova(data, dv, factor):
    # When the groups are balanced and have equal variances, the optimal
    # post-hoc test is the Tukey-HSD test (pingouin.pairwise_tukey()). If the
    # groups have unequal variances, the Games-Howell test is more adequate
    # (pingouin.pairwise_gameshowell()). Results have been tested against R.
    res_tab = pg.welch_anova(data=data, dv=dv, between=factor)
    res_tab = anovatable(res_tab)
    return res_tab


def run_mixedanova(
    data, dv, between, within, subject, correction="auto", effsize="np2"
):
    # Notes
    # Data are expected to be in long-format (even the repeated measures).
    # If your data is in wide-format, you can use the pandas.melt() function
    # to convert from wide to long format.

    # Warning
    # If the between-subject groups are unbalanced(=unequal sample sizes), a
    # type II ANOVA will be computed. Note however that SPSS, JAMOVI and JASP
    # by default return a type III ANOVA, which may lead to slightly different
    # results.
    res_tab = pg.mixed_anova(
        data=data,
        dv=dv,
        within=within,
        subject=subject,
        between=between,
        correction=correction,
        effsize=effsize,
    )
    res_tab = anovatable(res_tab)
    return res_tab


def run_friedman(data, dv, factor, subject, method="chisq"):
    # Friedman test for repeated measurements
    # The Friedman test is used for non-parametric (rank-based) one-way
    # repeated measures ANOVA

    # check df form ('long' or 'wide')
    # df_long = data.melt(ignore_index=False).reset_index()
    # if data.describe().shape[1] >= df_long.describe().shape[1]:
    #     res_tab = pg.friedman(data, method=method)
    # else:
    #     res_tab = pg.friedman(data=df_long, dv='value',
    #                           within="variable", subject="index", method=method)
    if "Wide" in df_wide_long(data):
        df_long = data.melt(ignore_index=False).reset_index()
        res_tab = pg.friedman(
            data=df_long,
            dv="value",
            within="variable",
            subject="index",
            method=method,
        )
    else:
        res_tab = pg.friedman(
            data, dv=dv, within=factor, subject=subject, method=method
        )
    res_tab = anovatable(res_tab)
    return res_tab


def run_kruskal(data, dv, factor):
    # Kruskal-Wallis H-test for independent samples
    res_tab = pg.kruskal(data=data, dv=dv, between=factor)
    res_tab = anovatable(res_tab)
    return res_tab


def df_wide_long(df):
    rows, columns = df.shape
    if columns > rows:
        return "Wide"
    elif rows > columns:
        return "Long"

 
def sort_rows_move_nan(arr, sort=False):
    # Handle edge cases where all values are NaN
    if np.all(np.isnan(arr)):
        return arr  # Return unchanged if the entire array is NaN

    if sort:
        # Replace NaNs with a temporary large value for sorting
        temp_value = (
            np.nanmax(arr[np.isfinite(arr)]) + 1 if np.any(np.isfinite(arr)) else np.inf
        )
        arr_no_nan = np.where(np.isnan(arr), temp_value, arr)

        # Sort each row
        sorted_arr = np.sort(arr_no_nan, axis=1)

        # Move NaNs to the end
        result_arr = np.where(sorted_arr == temp_value, np.nan, sorted_arr)
    else:
        result_rows = []
        for row in arr:
            # Separate non-NaN and NaN values
            non_nan_values = row[~np.isnan(row)]
            nan_count = np.isnan(row).sum()
            # Create a new row with non-NaN values followed by NaNs
            new_row = np.concatenate([non_nan_values, [np.nan] * nan_count])
            result_rows.append(new_row)
        # Convert the list of rows back into a 2D NumPy array
        result_arr = np.array(result_rows)

    # Remove rows/columns that contain only NaNs
    clean_arr = result_arr[~np.isnan(result_arr).all(axis=1)]
    clean_arr_ = clean_arr[:, ~np.isnan(clean_arr).all(axis=0)]

    return clean_arr_


def df2array(data: pd.DataFrame, x=None, y=None, hue=None, sort=False):
    if hue is None:
        a = []
        if sort:
            cat_x=np.sort(data[x].unique().tolist()).tolist()
        else:
            cat_x = data[x].unique().tolist()
        for i, x_ in enumerate(cat_x):
            new_ = data.loc[data[x] == x_, y].to_list()
            a = padcat(a, new_, axis=0)
        return sort_rows_move_nan(a).T
    else:
        a = []
        if sort:
            cat_x = np.sort(data[x].unique().tolist()).tolist()
            cat_hue = np.sort(data[hue].unique().tolist()).tolist()
        else:
            cat_x = data[x].unique().tolist()
            cat_hue = data[hue].unique().tolist()
        for i, x_ in enumerate(cat_x):
            for j, hue_ in enumerate(cat_hue):
                new_ = data.loc[(data[x] == x_) & (data[hue] == hue_), y].to_list()
                a = padcat(a, new_, axis=0)
        return sort_rows_move_nan(a).T

def array2df(data: np.ndarray):
    df = pd.DataFrame()
    df["group"] = (
        np.tile(
            ["group" + str(i) for i in range(1, data.shape[1] + 1)], [data.shape[0], 1]
        )
        .reshape(-1, 1, order="F")[:, 0]
        .tolist()
    )
    df["value"] = data.reshape(-1, 1, order="F")
    return df
def padcat(*args, fill_value=np.nan, axis=1, order="row"):
    """
    Concatenate vectors with padding.

    Parameters:
    *args : variable number of list or 1D arrays
        Input arrays to concatenate.
    fill_value : scalar, optional
        The value to use for padding the shorter lists (default is np.nan).
    axis : int, optional
        The axis along which to concatenate (0 for rows, 1 for columns, default is 1).
    order : str, optional
        The order for flattening when required: "row" or "column" (default is "row").

    Returns:
    np.ndarray
        A 2D array with the input arrays concatenated along the specified axis,
        padded with fill_value where necessary.
    """
    # Set the order for processing
    if "ro" in order.lower():
        order = "C"  # row-major order
    else:
        order = "F"  # column-major order

    # Process input arrays based on their dimensions
    processed_arrays = []
    for arg in args:
        arr = np.asarray(arg)
        if arr.ndim == 1:
            processed_arrays.append(arr)  # Keep 1D arrays as is
        elif arr.ndim == 2:
            if axis == 0:
                # If concatenating along rows, split 2D arrays into 1D arrays row-wise
                processed_arrays.extend(arr)
            elif axis == 1:
                # If concatenating along columns, split 2D arrays into 1D arrays column-wise
                processed_arrays.extend(arr.T)
            else:
                raise ValueError("axis must be 0 or 1")
        else:
            raise ValueError("Input arrays must be 1D or 2D")

    if axis == 0:
        # Concatenate along rows
        max_len = max(arr.size for arr in processed_arrays)
        result = np.full((len(processed_arrays), max_len), fill_value)
        for i, arr in enumerate(processed_arrays):
            result[i, : arr.size] = arr
    elif axis == 1:
        # Concatenate along columns
        max_len = max(arr.size for arr in processed_arrays)
        result = np.full((max_len, len(processed_arrays)), fill_value)
        for i, arr in enumerate(processed_arrays):
            result[: arr.size, i] = arr
    else:
        raise ValueError("axis must be 0 or 1")

    return result


# # Example usage:
# a = [1, np.nan]
# b = [1, 3, 4, np.nan, 2, np.nan]
# c = [1, 2, 3, 4, 5, 6, 7, 8, 10]
# d = padcat(a, b)
# result1 = padcat(d, c)
# result2 = padcat(a, b, c)
# print("Result of padcat(d, c):\n", result1)
# print("Result of padcat(a, b, c):\n", result2)
