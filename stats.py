from scipy.ndimage import convolve1d
from scipy.signal import savgol_filter
import pingouin as pg
from scipy import stats

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ==============FuncStars(ax,x1=1,x2=2, yscale=0.9, pval=0.01)====================================================
# Usage:
# FuncStars(ax, x1=2, x2=3, yscale=0.99, pval=0.02)
# =============================================================================

# FuncStars --v 0.1.1
def FuncStars(ax,
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
              report_loc=None):
    if ax is None:
        ax = plt.gca()
    if Ylim is None:
        Ylim = plt.gca().get_ylim()
    if Xlim is None:
        Xlim = ax.get_xlim()
    if report_loc is None and report is not None:
        report_loc = np.min(Ylim) + report_scale*np.abs(np.diff(Ylim))
    if report_scale > 0:
        report_scale = -np.abs(report_scale)
    yscale = np.float64(yscale)
    y_loc = np.min(Ylim) + yscale*(np.max(Ylim)-np.min(Ylim))
    xcenter = np.mean([x1, x2])
    # ns / *
    if alpha < pval:
        if nsshow == 'on':
            ns_str = f'p={round(pval, 3)}' if pval < 0.9 else 'ns'
            color = 'm' if pval < 0.1 else 'k'
            plt.text(xcenter, y_loc, ns_str,
                     ha='center', va='bottom',  # 'center_baseline',
                     fontsize=fontsize-6 if fontsize > 6 else fontsize,
                     fontname=fontname, color=color, rotation=rotation
                     # bbox=dict(facecolor=None, edgecolor=None, color=None, linewidth=None)
                     )
    elif 0.01 < pval <= alpha:
        plt.text(xcenter, y_loc, symbol,
                 ha='center', va='center_baseline',
                 fontsize=fontsize, fontname=fontname, color=symbolcolor)
    elif 0.001 < pval <= 0.01:
        plt.text(xcenter, y_loc, symbol * 2,
                 ha='center', va='center_baseline',
                 fontsize=fontsize, fontname=fontname, color=symbolcolor)
    elif 0 < pval <= 0.001:
        plt.text(xcenter, y_loc, symbol * 3,
                 ha='center', va='center_baseline',
                 fontsize=fontsize, fontname=fontname, color=symbolcolor)
    # lines indicators
    if linego:  # and 0 < pval <= 0.05:
        print(pval)
        print(linego)
        # horizontal line
        if yscale < 0.99:
            plt.plot([x1 + np.abs(np.diff(Xlim)) * 0.01,
                      x2 - np.abs(np.diff(Xlim)) * 0.01],
                     [y_loc - np.abs(np.diff(Ylim)) * .03,
                      y_loc - np.abs(np.diff(Ylim)) * .03],
                     linestyle=linestyle, color=linecolor, linewidth=linewidth)
            # vertical line
            plt.plot([x1 + np.abs(np.diff(Xlim)) * 0.01,
                      x1 + np.abs(np.diff(Xlim)) * 0.01],
                     [y_loc - np.abs(np.diff(Ylim)) * tailindicator[0],
                      y_loc - np.abs(np.diff(Ylim)) * .03],
                     linestyle=linestyle, color=linecolor, linewidth=linewidth)
            plt.plot([x2 - np.abs(np.diff(Xlim)) * 0.01,
                      x2 - np.abs(np.diff(Xlim)) * 0.01],
                     [y_loc - np.abs(np.diff(Ylim)) * tailindicator[1],
                      y_loc - np.abs(np.diff(Ylim)) * .03],
                     linestyle=linestyle, color=linecolor, linewidth=linewidth)
        else:
            plt.plot([x1 + np.abs(np.diff(Xlim)) * 0.01,
                      x2 - np.abs(np.diff(Xlim)) * 0.01],
                     [np.min(Ylim) + 0.95*(np.max(Ylim)-np.min(Ylim)) - np.abs(np.diff(Ylim)) * 0.002,
                      np.min(Ylim) + 0.95*(np.max(Ylim)-np.min(Ylim)) - np.abs(np.diff(Ylim)) * 0.002],
                     linestyle=linestyle, color=linecolor, linewidth=linewidth)
            # vertical line
            plt.plot([x1 + np.abs(np.diff(Xlim)) * 0.01,
                      x1 + np.abs(np.diff(Xlim)) * 0.01],
                     [np.min(Ylim) + 0.95*(np.max(Ylim)-np.min(Ylim)) - np.abs(np.diff(Ylim)) * tailindicator[0],
                      np.min(Ylim) + 0.95*(np.max(Ylim)-np.min(Ylim)) - np.abs(np.diff(Ylim)) * 0.002],
                     linestyle=linestyle, color=linecolor, linewidth=linewidth)
            plt.plot([x2 - np.abs(np.diff(Xlim)) * 0.01,
                      x2 - np.abs(np.diff(Xlim)) * 0.01],
                     [np.min(Ylim) + 0.95*(np.max(Ylim)-np.min(Ylim)) - np.abs(np.diff(Ylim)) * tailindicator[1],
                      np.min(Ylim) + 0.95*(np.max(Ylim)-np.min(Ylim)) - np.abs(np.diff(Ylim)) * 0.002],
                     linestyle=linestyle, color=linecolor, linewidth=linewidth)
    if values_below is not None:
        plt.text(xcenter, y_loc * (-0.1), values_below,
                 ha='center', va='bottom',  # 'center_baseline', rotation=rotation,
                 fontsize=fontsize_note, fontname=fontname, color='k')
    # report / comments
    if report is not None:
        plt.text(xcenter, report_loc, report,
                 ha='left', va='bottom',  # 'center_baseline', rotation=rotation,
                 fontsize=fontsize_note, fontname=fontname, color='.7')




def FuncCmpt(X1, X2, pmc='auto', pair='unpaired'):
    # output = {}

    # pmc correction: 'parametric'/'non-parametric'/'auto'
    # meawhile get the opposite setting (to compare the results)
    def corr_pmc(pmc):
        cfg_pmc = None
        if pmc.lower() in {'pmc', 'parametric'} and pmc.lower() not in {'npmc', 'nonparametric', 'non-parametric'}:
            cfg_pmc = 'parametric' 
        elif pmc.lower() in {'npmc', 'nonparametric', 'non-parametric'} and pmc.lower() not in {'pmc', 'parametric'}:
            cfg_pmc = 'non-parametric' 
        else:
            cfg_pmc = 'auto' 
        return cfg_pmc

    def corr_pair(pair):
        cfg_pair = None
        if 'pa' in pair.lower() and 'np' not in pair.lower():
            cfg_pair = 'paired'
        elif 'np' in pair.lower():
            cfg_pair = 'unpaired'
        return cfg_pair

    def check_normality(data):
        stat_shapiro, pval_shapiro = stats.shapiro(data)
        if pval_shapiro > 0.05:
            Normality = True
        else:
            Normality = False
        print(f'\n normally distributed\n') if Normality else print(
            f'\n NOT normally distributed\n')
        return Normality

    def sub_cmpt_2group(X1, X2, cfg_pmc='pmc', pair='unpaired'):
        output = {}
        nX1 = np.sum(~np.isnan(X1))
        nX2 = np.sum(~np.isnan(X2))
        if cfg_pmc == 'parametric' or cfg_pmc == 'auto':
            # VarType correction by checking variance Type via "levene"
            stat_lev, pval_lev = stats.levene(
                X1, X2, center='median', proportiontocut=0.05)
            VarType = True if pval_lev > 0.05 and nX1 == nX2 else False

            if 'np' in pair:  # 'unpaired'
                if VarType and Normality:
                    # The independent t-test requires that the dependent variable is approximately normally
                    # distributed within each group
                    # Note: Technically, it is the residuals that need to be normally distributed, but for
                    # an independent t-test, both will give you the same result.
                    stat_value, pval= stats.ttest_ind(
                        X1, X2, axis=0, equal_var=True, nan_policy='omit', alternative='two-sided')
                    notes_stat = 'unpaired t test'
                    notes_APA = f't({nX1+nX2-2})={round(stat_value, 5)},p={round(pval, 5)}'
                else:
                    # If the Levene's Test for Equality of Variances is statistically significant,
                    # which indicates that the group variances are unequal in the population, you
                    # can correct for this violation by not using the pooled estimate for the error
                    # term for the t-statistic, but instead using an adjustment to the degrees of
                    # freedom using the Welch-Satterthwaite method
                    stat_value, pval= stats.ttest_ind(
                        X1, X2, axis=0, equal_var=False, nan_policy='omit', alternative='two-sided')
                    notes_stat = 'Welchs t-test'
                    # note: APA FORMAT
                    notes_APA = f't({nX1+nX2-2})={round(stat_value, 5)},p={round(pval, 5)}'
            elif 'pa' in pair and 'np' not in pair:  # 'paired'
                # the paired-samples t-test is considered “robust” in handling violations of normality
                # to some extent. It can still yield valid results even if the data is not normally
                # distributed. Therefore, this test typically requires only approximately normal data
                stat_value, pval= stats.ttest_rel(
                    X1, X2, axis=0, nan_policy='omit', alternative='two-sided')
                notes_stat = 'paired t test'
                # note: APA FORMAT
                notes_APA = f't({sum([nX1-1])})={round(stat_value, 5)},p={round(pval, 5)}'
        elif cfg_pmc == 'non-parametric':
            if 'np' in pair:  # Perform Mann-Whitney
                stat_value, pval = stats.mannwhitneyu(
                    X1, X2, method='exact', nan_policy='omit')
                notes_stat = 'Mann-Whitney U'
                if nX1 == nX2:
                    notes_APA = f'U(n={nX1})={round(stat_value, 5)},p={round(pval, 5)}'
                else:
                    notes_APA = f'U(n1={nX1},n2={nX2})={round(stat_value, 5)},p={round(pval, 5)}'
            elif 'pa' in pair and 'np' not in pair:  # Wilcoxon signed-rank test
                stat_value, pval = stats.wilcoxon(
                    X1, X2, method='exact', nan_policy='omit')
                notes_stat = 'Wilcoxon signed-rank'
                if nX1 == nX2:
                    notes_APA = f'Z(n={nX1})={round(stat_value, 5)},p={round(pval, 5)}'
                else:
                    notes_APA = f'Z(n1={nX1},n2={nX2})={round(stat_value, 5)},p={round(pval, 5)}'

        # filling output
        output['stat'] = stat_value
        output['pval'] = pval
        output['method'] = notes_stat
        output['APA'] = notes_APA

        print(f"{output['method']}\n {notes_APA}\n\n")

        return output, pval

    Normality1 = check_normality(X1)
    Normality2 = check_normality(X2)
    Normality = True if all([Normality1, Normality2]) else False

    nX1 = np.sum(~np.isnan(X1))
    nX2 = np.sum(~np.isnan(X2))

    cfg_pmc = corr_pmc(pmc)
    cfg_pair = corr_pair(pair)

    output, p = sub_cmpt_2group(
        X1, X2, cfg_pmc=cfg_pmc, pair=cfg_pair)
    return p, output

# ======compare 2 group test===================================================
# # Example
# X1 = [19, 22, 16, 29, 24]
# X2 = [20, 11, 17, 12, 22]

# p, res= FuncCmpt(X1, X2, pmc='pmc', pair='unparrr')

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
def df_wide_long(df):
    rows, columns = df.shape 
    if columns > rows:
        return "Wide"
    elif rows > columns:
        return "Long"

def FuncMultiCmpt(pmc='pmc', pair='unpair', data=None, dv=None, factor=None,
                  ss_type=2, detailed=True, effsize='np2',
                  correction='auto', between=None, within=None,
                  subject=None, group=None
                  ):

    def corr_pair(pair):
        cfg_pair = None
        if 'pa' in pair.lower() and 'np' not in pair.lower():
            cfg_pair = 'paired'
        elif 'np' in pair.lower():
            cfg_pair = 'unpaired'
        elif 'mix' in pair.lower():
            cfg_pair = 'mix'
        return cfg_pair

    def check_normality(data):
        stat_shapiro, pval_shapiro = stats.shapiro(data)
        if pval_shapiro > 0.05:
            Normality = True
        else:
            Normality = False
        print(f'\n normally distributed\n') if Normality else print(
            f'\n NOT normally distributed\n')
        return Normality

    def corr_pmc(pmc):
        cfg_pmc = None
        if pmc.lower() in {'pmc', 'parametric'} and pmc.lower() not in {'upmc', 'npmc', 'nonparametric', 'non-parametric'}:
            cfg_pmc = 'parametric' 
        elif pmc.lower() in {'upmc', 'npmc', 'nonparametric', 'non-parametric'} and pmc.lower() not in {'pmc', 'parametric'}:
            cfg_pmc = 'non-parametric' 
        else:
            cfg_pmc = 'auto' 
        return cfg_pmc

    def extract_apa(res_tab):
        notes_APA = []
        if "ddof1" in res_tab:
            for irow in range(res_tab.shape[0]):
                note_tmp = f'{res_tab.Source[irow]}:F{round(res_tab.ddof1[irow]),round(res_tab.ddof2[irow])}={round(res_tab.F[irow], 5)},p={round(res_tab["p-unc"][irow], 5)}'
                notes_APA.append([note_tmp])
        elif "DF" in res_tab:
            print(res_tab.shape[0])
            for irow in range(res_tab.shape[0]-1):
                note_tmp = f'{res_tab.Source[irow]}:F{round(res_tab.DF[irow]),round(res_tab.DF[res_tab.shape[0]-1])}={round(res_tab.F[irow], 5)},p={round(res_tab["p-unc"][irow], 5)}'
                notes_APA.append([note_tmp])
            notes_APA.append(['NaN'])
        elif "DF1" in res_tab:  # in 'mix' case
            for irow in range(res_tab.shape[0]):
                note_tmp = f'{res_tab.Source[irow]}:F{round(res_tab.DF1[irow]),round(res_tab.DF2[irow])}={round(res_tab.F[irow], 5)},p={round(res_tab["p-unc"][irow], 5)}'
                notes_APA.append([note_tmp])
        return notes_APA

    def anovatable(res_tab):
        if 'df' in res_tab:  # statsmodels
            res_tab['mean_sq'] = res_tab[:]['sum_sq']/res_tab[:]['df']
            res_tab['est_sq'] = res_tab[:-1]['sum_sq'] / \
                sum(res_tab['sum_sq'])
            res_tab['omega_sq'] = (res_tab[:-1]['sum_sq']-(res_tab[:-1]['df'] *
                                                           res_tab['mean_sq'][-1]))/(sum(res_tab['sum_sq'])+res_tab['mean_sq'][-1])
        elif 'DF' in res_tab:
            res_tab['MS'] = res_tab[:]['SS']/res_tab[:]['DF']
            res_tab['est_sq'] = res_tab[:-1]['SS']/sum(res_tab['SS'])
            res_tab['omega_sq'] = (res_tab[:-1]['SS']-(res_tab[:-1]['DF'] *
                                                       res_tab['MS'][1]))/(sum(res_tab['SS'])+res_tab['MS'][1])
        if 'p-unc' in res_tab:
            if 'np2' in res_tab:
                res_tab['est_sq'] = res_tab['np2']
            if 'p-unc' in res_tab:
                res_tab['PR(>F)'] = res_tab['p-unc']
        return res_tab

    def run_anova(data, dv, factor, ss_type=2, detailed=True, effsize='np2'):
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
        res_tab = pg.anova(dv=dv, between=factor, data=data,
                           detailed=detailed, ss_type=ss_type, effsize=effsize)
        res_tab = anovatable(res_tab)
        return res_tab

    def run_rmanova(data, dv, factor, subject, correction='auto', detailed=True, effsize='ng2'):
        # One-way repeated-measures ANOVA using a long-format dataset.
        res_tab = pg.rm_anova(data=data, dv=dv, within=factor,
                              subject=subject, detailed=detailed, effsize=effsize)
        return res_tab

    def run_welchanova(data, dv, factor):
        # When the groups are balanced and have equal variances, the optimal
        # post-hoc test is the Tukey-HSD test (pingouin.pairwise_tukey()). If the
        # groups have unequal variances, the Games-Howell test is more adequate
        # (pingouin.pairwise_gameshowell()). Results have been tested against R.
        res_tab = pg.welch_anova(data=data, dv=dv, between=factor)
        res_tab = anovatable(res_tab)
        return res_tab

    def run_mixedanova(data, dv, between, within, subject, correction='auto', effsize='np2'):
        # Notes
        # Data are expected to be in long-format (even the repeated measures).
        # If your data is in wide-format, you can use the pandas.melt() function
        # to convert from wide to long format.

        # Warning
        # If the between-subject groups are unbalanced(=unequal sample sizes), a
        # type II ANOVA will be computed. Note however that SPSS, JAMOVI and JASP
        # by default return a type III ANOVA, which may lead to slightly different
        # results.
        res_tab = pg.mixed_anova(data=data, dv=dv, within=within, subject=subject,
                                 between=between, correction=correction, effsize=effsize)
        res_tab = anovatable(res_tab)
        return res_tab

    def run_friedman(data, dv, factor, subject, method='chisq'):
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
            res_tab = pg.friedman(data=df_long, dv='value',
                                    within="variable", subject="index", method=method)
        else:
            res_tab = pg.friedman(data, dv=dv, within=factor, subject=subject,method=method)
        res_tab = anovatable(res_tab)
        return res_tab

    def run_kruskal(data, dv, factor):
        # Kruskal-Wallis H-test for independent samples
        res_tab = pg.kruskal(data=data, dv=dv, between=factor)
        res_tab = anovatable(res_tab)
        return res_tab

    # Normality Check:
    # Conduct normality tests (Shapiro-Wilk) for each group.
    # If the data is approximately normally distributed, ANOVA is robust to
    # moderate departures from normality, especially with larger sample sizes.

    # print(data[factor])
    # print(type(data[factor]))
    # print(len(data[factor].columns))
    # print(data[factor].nunique())
    # print(data[factor[0]])
    # print(data[factor[0]].unique())
    if group is None:
        group = factor

    # print(f'\ngroup is :\n{data[group]},\ndv is :\n{dv}\n')
    norm_array = []
    for sub_group in data[group].unique():
        norm_curr = check_normality(
            data.loc[data[group] == sub_group, dv])
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
    variance_all = pg.homoscedasticity(
        data, dv=dv, group=group, method='levene', alpha=0.05)
    res_levene = True if variance_all.iloc[0,1] > 0.05 else False
    # =============================================================================
    # # ANOVA Assumptions:
    # # Ensure that the assumptions of independence, homogeneity of variances, and
    # # normality are reasonably met before proceeding.
    # =============================================================================
    notes_norm = 'normally' if norm_all else 'NOT-normally'
    notes_variance = 'equal' if res_levene else 'unequal'
    print(f'Data is {notes_norm} distributed, shows {notes_variance} variance')

    cfg_pmc = corr_pmc(pmc)
    cfg_pair = corr_pair(pair)
    output = {}
    if (cfg_pmc == 'parametric') or (cfg_pmc == 'auto'):
        if 'np' in cfg_pair:  # 'unpaired'
            if cfg_pmc == 'auto':
                if norm_all:
                    if res_levene:
                        res_tab = run_anova(data, dv, factor, ss_type=ss_type,
                                            detailed=True, effsize='np2')
                        notes_stat = f'{data[factor].nunique()} Way ANOVA'
                        notes_APA = extract_apa(res_tab)

                    else:
                        res_tab = run_welchanova(data, dv, factor)
                        notes_stat = f'{data[factor].nunique()} Way Welch ANOVA'
                        notes_APA = extract_apa(res_tab)

                else:

                    res_tab = run_kruskal(data, dv, factor)
                    notes_stat = f'Non-parametric Kruskal: {data[factor].nunique()} Way ANOVA'
                    notes_APA = extract_apa(res_tab)

            elif cfg_pmc == 'parametric':
                res_tab = run_anova(data, dv, factor, ss_type=ss_type,
                                    detailed=True, effsize='np2')
                notes_stat = f'{data[factor].nunique()} Way ANOVA'
                notes_APA = extract_apa(res_tab)

        elif 'pa' in cfg_pair and 'np' not in cfg_pair:  # 'paired'
            res_tab = run_rmanova(data, dv, factor, subject, correction='auto',
                                  detailed=True, effsize='ng2')
            notes_stat = f'{data[factor].nunique()} Way Repeated measures ANOVA'
            notes_APA = extract_apa(res_tab)

        elif 'mix' in cfg_pair or 'both' in cfg_pair:
            res_tab = run_mixedanova(data, dv, between, within, subject)
            # notes_stat = f'{len(sum(len(between)+sum(len(within))))} Way Mixed ANOVA'
            notes_stat = ""
            # n_inter = res_tab.loc(res_tab["Source"] == "Interaction")
            # print(n_inter)
            notes_APA = extract_apa(res_tab)

    elif cfg_pmc == 'non-parametric':
        if 'np' in cfg_pair:  # 'unpaired'
            res_tab = run_kruskal(data, dv, factor)
            notes_stat = f'Non-parametric Kruskal: {data[factor].nunique()} Way ANOVA'
            notes_APA = f'H({res_tab.ddof1[0]},n={data.shape[0]})={round(res_tab.H[0], 5)},p={round(res_tab["p-unc"][0], 5)}'

        elif 'pa' in cfg_pair and 'np' not in cfg_pair:  # 'paired'
            res_tab = run_friedman(data, dv, factor, subject, method='chisq')
            notes_stat = f'Non-parametric {data[factor].nunique()} Way Friedman repeated measures ANOVA'
            notes_APA = f'X^2({res_tab.ddof1[0]})={round(res_tab.Q[0], 5)},p={round(res_tab["p-unc"][0], 5)}'

    # =============================================================================
    # # Post-hoc
    # Post-Hoc Tests (if significant):
    # If ANOVA indicates significant differences, perform post-hoc tests (e.g.,
    # Tukey's HSD, Bonferroni, or Scheffé) to identify which groups differ from each other.
    # # https://pingouin-stats.org/build/html/generated/pingouin.pairwise_tests.html
    # =============================================================================
    go_pmc = True if cfg_pmc == 'parametric' else False
    go_subject = subject if ('pa' in cfg_pair) and (
        'np' not in cfg_pair) else None
    go_mix_between = between if ('mix' in cfg_pair) or (
        'both' in cfg_pair) else None
    go_mix_between = None if ('pa' in cfg_pair) or (
        'np' not in cfg_pair) else factor
    go_mix_within = within if ('mix' in cfg_pair) or (
        'both' in cfg_pair) else None
    go_mix_within = factor if ('pa' in cfg_pair) or (
        'np' not in cfg_pair) else None
    if res_tab['p-unc'][0] <= .05:
        # Pairwise Comparisons
        method_post_hoc = [
            "bonf",  # 'bonferroni',  # : one-step correction
            "sidak",  # one-step correction
            "holm",  # step-down method using Bonferroni adjustments
            "fdr_bh",  # Benjamini/Hochberg (non-negative)
            "fdr_by",  # Benjamini/Yekutieli (negative)
        ]
        res_posthoc = pd.DataFrame()
        for met in method_post_hoc:
            post_curr = pg.pairwise_tests(data=data, dv=dv, between=go_mix_between, within=go_mix_within, subject=go_subject, parametric=go_pmc, marginal=True, alpha=0.05, alternative='two-sided',
                                          padjust=met)
            res_posthoc = pd.concat([res_posthoc, post_curr],
                                    ignore_index=True)
    else:
        res_posthoc = None
    output['res_posthoc'] = res_posthoc
    # =============================================================================
    #     # filling output
    # =============================================================================

    pd.set_option('display.max_columns', None)
    output['stat'] = notes_stat
    # print(output['APA'])
    output['APA'] = notes_APA
    output['pval'] = res_tab['p-unc']
    output['res_tab'] = res_tab
    if res_tab.shape[0] == len(notes_APA):
        output['res_tab']['APA'] = output['APA']  # note APA in the table
    # print(output['stat'])
    # print(output['res_tab'])
    return output


# =============================================================================
# # One-way ANOVA
# =============================================================================
# url = "http://stats191.stanford.edu/data/rehab.csv"
# rehab_table = pd.read_table(url, delimiter=",")
# rehab_table.to_csv("rehab.table")
# fig, ax = plt.subplots(figsize=(8, 6))
# fig = rehab_table.boxplot("Time", "Fitness", ax=ax, grid=False)
# # fig, ax = plt.subplots(figsize=(8, 6))
# # set_pub()
# # sns.boxenplot(x="Time",y="Fitness",data = rehab_table)

# out2 = FuncMultiCmpt(pmc='pmc', pair='unpair',
#                       data=rehab_table, dv='Time', factor='Fitness')
# # print(out2['res_tab'])
# # print(out2['APA'])
# out2['res_posthoc']
# out2['res_posthoc']['p-unc'][0]
# out2['res_posthoc']['p-adjust'][0]
# out2['res_posthoc']['p-corr'][0]


# =============================================================================
# # Interactions and ANOVA
# https://www.statsmodels.org/dev/examples/notebooks/generated/interactions_anova.html
# url = "http://stats191.stanford.edu/data/salary.table"
# fh = urlopen(url)
# df = pd.read_table(fh)
# out1 = FuncMultiCmpt(pmc='pmc', pair='unpaired', data=df,
#                      dv='S', factor=['X', 'E', 'M'], group='M')
# # # two-way anova
# # https://www.statology.org/two-way-anova-python/
# # =============================================================================
# # df = pd.DataFrame({'water': np.repeat(['daily', 'weekly'], 15),
# #                    'sun': np.tile(np.repeat(['low', 'med', 'high'], 5), 2),
# #                    'height': [6, 6, 6, 5, 6, 5, 5, 6, 4, 5,
# #                               6, 6, 7, 8, 7, 3, 4, 4, 4, 5,
# #                               4, 4, 4, 4, 4, 5, 6, 6, 7, 8]})
# # out1 = FuncMultiCmpt(pmc='pmc', pair='unpaired', data=df,
# #                       dv='height', factor=['water','sun'],group='water')


# =============================================================================
# # two way anova
# https://www.geeksforgeeks.org/how-to-perform-a-two-way-anova-in-python/
# =============================================================================
# df1=pd.DataFrame({'Fertilizer': np.repeat(['daily', 'weekly'], 15),
#                           'Watering': np.repeat(['daily', 'weekly'], 15),
#                           'height': [14, 16, 15, 15, 16, 13, 12, 11,
#                                       14, 15, 16, 16, 17, 18, 14, 13,
#                                       14, 14, 14, 15, 16, 16, 17, 18,
#                                       14, 13, 14, 14, 14, 15]})

# df1['subject'] = np.tile(range(0, 15), (1, 2)).T
# out1 = FuncMultiCmpt(pmc='pmc', pair='unpaired', data=df1,
#                       dv='height', factor=['Fertilizer','Watering'],group='Watering')
# # print(out1['stat'])
# # print(out1['res_tab'])

# =============================================================================
# # welch anova
# https://www.geeksforgeeks.org/how-to-perform-welchs-anova-in-python/
# =============================================================================
# df = pd.DataFrame({'score': [64, 66, 68, 75, 78, 94, 98, 79, 71, 80,
#                              91, 92, 93, 90, 97, 94, 82, 88, 95, 96,
#                              79, 78, 88, 94, 92, 85, 83, 85, 82, 81],
#                    'group': np.repeat(['strat1', 'strat2', 'strat3'],repeats=10)})
# out1 = FuncMultiCmpt(pmc='auto',pair='unpaired',data=df, dv='score', factor='group', group='group')
# =============================================================================
# # two way anova
# https://www.statology.org/two-way-anova-python/
# =============================================================================
# df = pd.DataFrame({'water': np.repeat(['daily', 'weekly'], 15),
#                    'sun': np.tile(np.repeat(['low', 'med', 'high'], 5), 2),
#                    'height': [6, 6, 6, 5, 6, 5, 5, 6, 4, 5,
#                               6, 6, 7, 8, 7, 3, 4, 4, 4, 5,
#                               4, 4, 4, 4, 4, 5, 6, 6, 7, 8]})
# df['subject'] = np.tile(range(0, 15), (1, 2)).T
# out1 = FuncMultiCmpt(pmc='pmc', pair='unpaired', data=df,
#                      dv='height', factor=['water', 'sun'], subject='subject', group='water')
# # print(out1['stat'])
# # print(out1['res_tab'])

# =============================================================================
# # 3-way ANOVA
# =============================================================================
# df = pd.DataFrame({'program': np.repeat([1, 2], 20),
#                    'gender': np.tile(np.repeat(['M', 'F'], 10), 2),
#                    'division': np.tile(np.repeat([1, 2], 5), 4),
#                    'height': [7, 7, 8, 8, 7, 6, 6, 5, 6, 5,
#                               5, 5, 4, 5, 4, 3, 3, 4, 3, 3,
#                               6, 6, 5, 4, 5, 4, 5, 4, 4, 3,
#                               2, 2, 1, 4, 4, 2, 1, 1, 2, 1]})
# df['subject'] = np.tile(range(0, 20), (1, 2)).T
# out1 = FuncMultiCmpt(pmc='pmc', pair='unpaired', data=df,
#                      dv='height', factor=['gender', 'program', 'division'], subject='subject', group='program')
# # print(out1['stat'])
# # print(out1['res_tab'])

# =============================================================================
# # Repeated Measures ANOVA in Python
# =============================================================================
# df = pd.DataFrame({'patient': np.repeat([1, 2, 3, 4, 5], 4),
#                     'drug': np.tile([1, 2, 3, 4], 5),
#                     'response': [30, 28, 16, 34,
#                                 14, 18, 10, 22,
#                                 24, 20, 18, 30,
#                                 38, 34, 20, 44,
#                                 26, 28, 14, 30]})
# # df['subject'] = np.tile(range(0, 20), (1, 2)).T
# out1 = FuncMultiCmpt(pmc='pmc', pair='paired', data=df,
#                       dv='response', factor=['drug'], subject='patient', group='drug')
# print(out1['stat'])
# print(out1['res_tab'])
# print(out1['APA'])

# =============================================================================
# # repeated anova
# https://www.geeksforgeeks.org/how-to-perform-a-repeated-measures-anova-in-python/
# =============================================================================
# df = pd.DataFrame({'Cars': np.repeat([1, 2, 3, 4, 5], 4),
#                'Engine Oil': np.tile([1, 2, 3, 4], 5),
#                'Mileage': [36, 38, 30, 29,
#                            34, 38, 30, 29,
#                            34, 28, 38, 32,
#                            38, 34, 20, 44,
#                            26, 28, 34, 50]})
# out1 = FuncMultiCmpt(pmc='pmc', pair='paired', data=df,
#                  dv='Mileage', factor=['Engine Oil'], subject='Cars', group='Cars')
# =============================================================================
# #two-way repeated anova
# =============================================================================
# df = pd.read_csv(
#     "https://reneshbedre.github.io/assets/posts/anova/plants_leaves_two_within.csv")
# df
# # df['subject'] = np.tile(range(0, 20), (1, 2)).T
# out1 = FuncMultiCmpt(pmc='pmc', pair='paired', data=df,
#                       dv='num_leaves', factor=['year', 'time'], subject='plants', group='year')
# print(out1['stat'])
# print(out1['res_tab'])
# print(out1['APA'])

# =============================================================================
# # repeated anova
# =============================================================================
# df = pd.read_csv('/Users/macjianfeng/Desktop/test.csv')
# df.head()
# df.loc[df['animal'].str.contains('Sleep'), 'experiment'] = 'sleep'
# df.loc[df['animal'].str.contains('Wake'), 'experiment'] = 'wake'
# df.loc[df['variable'].str.contains('hypo'), 'region'] = 'hypo'
# df.loc[df['variable'].str.contains('cort'), 'region'] = 'cort'
# df
# for i in range(4):
#     match i:
#         case 0:
#             prot_name = 'A1'
#         case 1:
#             prot_name = 'A2'
#         case 2:
#             prot_name = '845'
#         case 3:
#             prot_name = '831'
#     df_tmp = df[df["variable"].str.contains(prot_name)]
#     df_tmp['protein'] = prot_name
#     df_tmp = df_tmp.reset_index()
#     print(df_tmp)

# out1 = FuncMultiCmpt(pmc='pmc', pair='mix', data=df_tmp,
#                      dv='value', between='experiment', within='region', subject='animal', group='experiment')
# print(out1['stat'])
# print(out1['res_tab'])
# # =============================================================================
# One-way ANOVA
# df1 = pd.read_csv('/Users/macjianfeng/Desktop/Book2.csv')
# df2 = df1.melt()
# out1 = FuncMultiCmpt(pmc='npmc', pair='unpaired', data=df2,
#                      dv='libido', factor=['brand x', 'brand y', 'brand z'], subject='participant')
# print(out1['stat'])
# print(out1['res_tab'])
# =============================================================================


# =============================================================================
# # #One-way ANOVA new example: https://www.pythonfordatascience.org/anova-python/
# =============================================================================
# df1 = pd.read_csv(
#     "https://raw.githubusercontent.com/researchpy/Data-sets/master/difficile.csv")
# df1.drop('person', axis=1, inplace=True)
# # Recoding value from numeric to string
# df1['dose'].replace({1: 'placebo', 2: 'low', 3: 'high'}, inplace=True)
# df1.head(10)

# out3= FuncMultiCmpt(pmc='pmc', data=df1, dv='libido', factor='dose')
# # print(out3['res_tab'])
# # # print(out3['res_posthoc'])
# # print(out3['APA'])

# =============================================================================
# https://lifewithdata.com/2023/06/08/how-to-perform-a-two-way-anova-in-python/
# =============================================================================
# data = {
#     'Diet': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C'],
#     'Workout': ['Low', 'Medium', 'High', 'Low', 'Medium', 'High', 'Low', 'Medium', 'High', 'Low', 'Medium', 'High'],
#     'WeightLoss': [3, 4, 5, 3.2, 5, 6, 5.2, 6, 5.5, 4, 5.5, 6.2]
# }
# df = pd.DataFrame(data)
# out4= FuncMultiCmpt(pmc='pmc', pair='unpaired',data=df, dv='WeightLoss', factor=['Diet','Workout'],group='Diet')

# =============================================================================
# # convert to list to string
# =============================================================================