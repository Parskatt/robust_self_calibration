import cv2
import matlab.engine
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.spatial.transform import Rotation
from tqdm import tqdm

from eval.synth.synth_scenarios import get_scene, noncoplanar_scene, coplanar_scene, set_scene, get_pp_err
from matlab_utils.engine_calls import ours_uncal, ours_single, ours_single_uncal
from methods.base import bougnoux_original, get_focal_sturm
from methods.fetzer import fetzer_focal_only
from methods.hartley import hartley, hartley_sturm
from utils.plot import custom_dodge_boxplot

def uncal_coplanarity_plot(load=True, ylim=(0, 1400), repeats=20, legend_visible=True):
    angles = [15, 10, 5, 3, 2, 1, 0]
    path = 'saved/synth/uncal_coplanarity.pkl'

    f1 = 600
    f1_prior = 700
    f2 = 400

    sigma = 1.0

    eng = matlab.engine.start_matlab()
    s = eng.genpath('matlab_utils')
    eng.addpath(s, nargout=0)

    df = pd.DataFrame(columns=['angle', 'f_1', 'Method'])

    def angle_str(angle):
        return '$\mathcal{C}(' + str(angle) + '°, 0)$'

    if load:
        df = pd.read_pickle(path)
    else:
        for angle in angles:
            f1, f2, R, t = set_scene(f1, f2, angle, 0)
            x1, x2, _ = get_scene(f1, f2, R, t, 100, sigma_p=10)

            for _ in tqdm(range(repeats)):
                xx1 = x1 + sigma * np.random.randn(*(x1.shape))
                xx2 = x2 + sigma * np.random.randn(*(x1.shape))
                F, mask = cv2.findFundamentalMat(xx1, xx2, cv2.USAC_MAGSAC)
                mask = mask.ravel().astype(np.bool)

                df = df.append({'angle': angle_str(angle), 'f_1': ours_uncal(eng, F, f1_prior, f2)[0], 'Method': 'Ours'}, ignore_index=True)
                df = df.append({'angle': angle_str(angle), 'f_1': hartley(F, xx1[mask], xx2[mask], f1_prior, f2)[0], 'Method': 'Hartley'}, ignore_index=True)
                df = df.append({'angle': angle_str(angle), 'f_1': fetzer_focal_only(F, f1_prior, f2)[0], 'Method': 'Fetzer'}, ignore_index=True)
                df = df.append({'angle': angle_str(angle), 'f_1': np.sqrt(bougnoux_original(F)[0]), 'Method': 'Bougnoux'}, ignore_index=True)

        df.to_pickle(path)

    for x, _ in enumerate(angles):
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25)

    order = [angle_str(x) for x in angles]
    # sns.boxplot(data=df, x='f_1 Prior', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    custom_dodge_boxplot(data=df, x='angle', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    plt.ylim(ylim)
    axes = plt.gca()
    xlim = (-0.5, len(angles) - 0.5)
    plt.xlim(xlim)
    plt.ylim(ylim)

    plt.legend(loc='upper left')
    l_gt, = plt.plot(xlim, [f1, f1], 'k--')

    legend_1 = axes.get_legend()
    l_prior, = plt.plot([-0.5, len(angles) - 0.5], [f1_prior, f1_prior], linestyle='--', color='0.8', zorder=2.0)
    for x, _ in enumerate(angles):
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25, zorder=2.0)

    handles = [l_gt, l_prior]
    labels = ['GT $f_1$', 'Prior $f_1$']
    axes.legend(handles, labels, loc='upper right')
    if legend_visible:
        axes.add_artist(legend_1)
    else:
        axes.get_legend().remove()

    plt.ylabel('Estimated $f_1$')
    axes.set(xlabel='Camera Configuration')
    # plt.xlabel('Distance to coplanarity (multiples of $f_2$)')
    # plt.xlabel('Y-coordinate of the second camera center')
    plt.tick_params(bottom = False)

    plt.ylabel('Estimated $f_1$')
    # plt.xlabel('Camera configuration')
    plt.tick_params(bottom = False)


def uncal_coplanarity_y_plot(load=True, ylim=(0, 1400), repeats=20, legend_visible=True):
    ys = [300, 200, 100, 50, 25, 0]
    path = 'saved/synth/uncal_coplanarity_y.pkl'

    f1 = 600
    f1_prior = 700
    f2 = 400
    sigma = 1.0

    eng = matlab.engine.start_matlab()
    s = eng.genpath('matlab_utils')
    eng.addpath(s, nargout=0)

    df = pd.DataFrame(columns=['y', 'f_1', 'Method'])

    def y_str(y):
        return '$\mathcal{C}(0\degree, ' + str(y) + ')$'


    if load:
        df = pd.read_pickle(path)
    else:
        for y in ys:
            f1, f2, R, t = set_scene(f1, f2, theta=0, y=y)

            for _ in tqdm(range(repeats)):
                x1, x2, _ = get_scene(f1, f2, R, t, 100, sigma_p=10)

                xx1 = x1 + sigma * np.random.randn(*(x1.shape))
                xx2 = x2 + sigma * np.random.randn(*(x1.shape))

                F, mask = cv2.findFundamentalMat(xx1, xx2, cv2.USAC_MAGSAC)
                mask = mask.ravel().astype(np.bool)

                # df = df.append({'y': '{} $f_2$'.format(y), 'f_1': kukelova_uncal(eng, F, f1_prior, f2)[0], 'Method': 'Ours'}, ignore_index=True)
                # df = df.append({'y': '{} $f_2$'.format(y), 'f_1': hartley(F, xx1[mask], xx2[mask], f1_prior, f2)[0], 'Method': 'Hartley'}, ignore_index=True)
                # df = df.append({'y': '{} $f_2$'.format(y), 'f_1': fetzer_focal_only(F, f1_prior, f2)[0], 'Method': 'Fetzer'}, ignore_index=True)
                # df = df.append({'y': '{} $f_2$'.format(y), 'f_1': np.sqrt(bougnoux_original(F)[0]), 'Method': 'Bougnoux'}, ignore_index=True)

                df = df.append({'y': y_str(y), 'f_1': ours_uncal(eng, F, f1_prior, f2)[0], 'Method': 'Ours'}, ignore_index=True)
                df = df.append({'y': y_str(y), 'f_1': hartley(F, xx1[mask], xx2[mask], f1_prior, f2)[0], 'Method': 'Hartley'}, ignore_index=True)
                df = df.append({'y': y_str(y), 'f_1': fetzer_focal_only(F, f1_prior, f2)[0], 'Method': 'Fetzer'}, ignore_index=True)
                df = df.append({'y': y_str(y), 'f_1': np.sqrt(bougnoux_original(F)[0]), 'Method': 'Bougnoux'}, ignore_index=True)

        df.to_pickle(path)

    for x, _ in enumerate(ys):
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25)

    # order = ['{} $f_2$'.format(y) for y in ys]
    order = [y_str(y) for y in ys]
    # sns.boxplot(data=df, x='f_1 Prior', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    custom_dodge_boxplot(data=df, x='y', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    plt.ylim(ylim)
    axes = plt.gca()
    xlim = (-0.5, len(ys) - 0.5)
    plt.xlim(xlim)
    plt.ylim(ylim)

    plt.legend(loc='upper left')
    l_gt, = plt.plot(xlim, [f1, f1], 'k--')

    legend_1 = axes.get_legend()
    l_prior, = plt.plot([-0.5, len(ys) - 0.5], [f1_prior, f1_prior], linestyle='--', color='0.8', zorder=2.0)
    for x, _ in enumerate(ys):
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25, zorder=2.0)

    handles = [l_gt, l_prior]
    labels = ['GT $f_1$', 'Prior $f_1$']
    axes.legend(handles, labels, loc='upper right')
    if legend_visible:
        axes.add_artist(legend_1)
    else:
        axes.get_legend().remove()

    plt.ylabel('Estimated $f_1$')
    axes.set(xlabel='Camera Configuration')
    # plt.xlabel('Distance to coplanarity (multiples of $f_2$)')
    # plt.xlabel('\mathcal{C}_T(y)')
    plt.tick_params(bottom = False)


def uncal_noise_box_plot(load=True, ylim=(0, 1400), repeats=20, legend_visible=True):
    df = pd.DataFrame(columns = ['Noise', 'f_1', 'Method'])

    noise_vals = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]

    path = 'saved/synth/uncal_noise.pkl'

    thetas = np.random.rand(repeats) * 30 - 15
    ys = np.random.rand(repeats) * 400 - 200
    # thetas = np.random.randn(repeats) * 10.0
    # ys = np.random.randn(repeats) * 200

    f1 = 600
    f2 = 400

    scenes = [set_scene(f1, f2, theta=theta, y=y) for theta, y in zip(thetas, ys)]
    xs = [get_scene(*scene, 100, sigma_p=10) for scene in scenes]

    f1_prior = 700
    f2_prior = 400

    eng = matlab.engine.start_matlab()
    s = eng.genpath('matlab_utils')
    eng.addpath(s, nargout=0)

    if load:
        df = pd.read_pickle(path)
    else:
        for sigma in tqdm(noise_vals):
            for x1, x2, _ in xs:
                xx1 = x1 + sigma * np.random.randn(*(x1.shape))
                xx2 = x2 + sigma * np.random.randn(*(x1.shape))
                F, mask = cv2.findFundamentalMat(xx1, xx2, cv2.USAC_MAGSAC)
                mask = mask.ravel().astype(np.bool)

                df = df.append({'Noise': sigma, 'f_1': ours_uncal(eng, F, f1_prior, f2_prior)[0], 'Method': 'Ours'}, ignore_index = True)
                df = df.append({'Noise': sigma, 'f_1': hartley(F, xx1[mask], xx2[mask], f1_prior, f2_prior)[0] , 'Method': 'Hartley'}, ignore_index = True)
                df = df.append({'Noise': sigma, 'f_1': fetzer_focal_only(F, f1_prior, f2_prior)[0], 'Method': 'Fetzer'}, ignore_index = True)
                df = df.append({'Noise': sigma, 'f_1': np.sqrt(bougnoux_original(F)[0]) , 'Method': 'Bougnoux'}, ignore_index = True)

        df.to_pickle(path)

    order = [sigma for sigma in noise_vals]
    custom_dodge_boxplot(data=df, x='Noise', y='f_1', hue='Method', dodge=True, order=order, width=0.8)

    axes = plt.gca()
    xlim = (-0.5, len(noise_vals) - 0.5)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend(loc='upper left')
    l_gt, = plt.plot(xlim, [f1, f1], 'k--')


    legend_1 = axes.get_legend()

    l_prior, = plt.plot([-0.5,  len(noise_vals) - 0.5], [f1_prior, f1_prior], linestyle='--', color='0.8', zorder=2.0)
    for x, _ in enumerate(noise_vals):
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25, zorder=2.0)

    handles = [l_gt, l_prior]
    labels = ['GT $f_1$', 'Prior $f_1$']
    axes.legend(handles, labels, loc='upper right')
    if legend_visible:
        axes.add_artist(legend_1)
    else:
        axes.get_legend().remove()

    plt.ylabel('Estimated $f_1$')
    plt.xlabel('$\sigma_n$')
    plt.tick_params(bottom = False)


def uncal_principal_boxplot(load=True, ylim=(0, 1400), repeats=20, legend_visible=True):
    df = pd.DataFrame(columns = ['Noise', 'f_1', 'Method'])

    noise_vals = [0, 2, 5, 10, 20, 50]

    path = 'saved/synth/uncal_principal.pkl'

    thetas = np.random.rand(repeats) * 30 - 15
    ys = np.random.rand(repeats) * 400 - 200
    # thetas = np.random.randn(repeats) * 10.0
    # ys = np.random.randn(repeats) * 200

    f1 = 600
    f2 = 400

    scenes = [set_scene(f1, f2, theta=theta, y=y) for theta, y in zip(thetas, ys)]
    xs = [get_scene(*scene, 100, sigma_p=0) for scene in scenes]

    f1_prior = 700
    f2_prior = 400
    
    sigma = 1.0

    eng = matlab.engine.start_matlab()
    s = eng.genpath('matlab_utils')
    eng.addpath(s, nargout=0)

    if load:
        df = pd.read_pickle(path)
    else:
        for sigma_p in tqdm(noise_vals):
            for x1, x2, _ in xs:
                p_err_1 = get_pp_err(sigma_p)
                p_err_2 = get_pp_err(sigma_p)

                xx1 = x1 + sigma * np.random.randn(*(x1.shape)) - p_err_1
                xx2 = x2 + sigma * np.random.randn(*(x1.shape)) - p_err_2
                F, mask = cv2.findFundamentalMat(xx1, xx2, cv2.USAC_MAGSAC)
                mask = mask.ravel().astype(np.bool)

                df = df.append({'Noise': sigma_p, 'f_1': ours_uncal(eng, F, f1_prior, f2_prior)[0], 'Method': 'Ours'}, ignore_index = True)
                df = df.append({'Noise': sigma_p, 'f_1': hartley(F, xx1[mask], xx2[mask], f1_prior, f2_prior)[0] , 'Method': 'Hartley'}, ignore_index = True)
                df = df.append({'Noise': sigma_p, 'f_1': fetzer_focal_only(F, f1_prior, f2_prior)[0], 'Method': 'Fetzer'}, ignore_index = True)
                df = df.append({'Noise': sigma_p, 'f_1': np.sqrt(bougnoux_original(F)[0]) , 'Method': 'Bougnoux'}, ignore_index = True)

        df.to_pickle(path)

    order = [sigma for sigma in noise_vals]
    custom_dodge_boxplot(data=df, x='Noise', y='f_1', hue='Method', dodge=True, order=order, width=0.8)

    axes = plt.gca()
    xlim = (-0.5, len(noise_vals) - 0.5)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend(loc='upper left')
    l_gt, = plt.plot(xlim, [f1, f1], 'k--')


    legend_1 = axes.get_legend()

    l_prior, = plt.plot([-0.5,  len(noise_vals) - 0.5], [f1_prior, f1_prior], linestyle='--', color='0.8', zorder=2.0)
    for x, _ in enumerate(noise_vals):
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25, zorder=2.0)

    handles = [l_gt, l_prior]
    labels = ['GT $f_1$', 'Prior $f_1$']
    axes.legend(handles, labels, loc='upper right')
    if legend_visible:
        axes.add_artist(legend_1)
    else:
        axes.get_legend().remove()

    plt.ylabel('Estimated $f_1$')
    plt.xlabel('$\sigma_p$')
    plt.tick_params(bottom = False)


def uncal_prior_boxplot(load=True, ylim=(0, 1400), repeats=20, legend_visible=True):
    df = pd.DataFrame(columns = ['Noise', 'f_1', 'Method'])

    path = 'saved/synth/uncal_prior.pkl'

    eng = matlab.engine.start_matlab()
    s = eng.genpath('matlab_utils')
    eng.addpath(s, nargout=0)

    priors = [300, 480, 540, 600, 660, 720, 780, 900, 1200]

    sigma = 1.0

    thetas = np.random.rand(repeats) * 30 - 15
    ys = np.random.rand(repeats) * 400 - 200

    # thetas = np.random.randn(repeats) * 10.0
    # ys = np.random.randn(repeats) * 200

    f1 = 600
    f2 = 400

    scenes = [set_scene(f1, f2, theta=theta, y=y) for theta, y in zip(thetas, ys)]
    xs = [get_scene(*scene, 100, sigma_p=10) for scene in scenes]

    if load:
        df = pd.read_pickle(path)
    else:
        for f_1_prior in tqdm(priors):
            for x1, x2, _ in xs:
                xx1 = x1 + sigma * np.random.randn(*(x1.shape))
                xx2 = x2 + sigma * np.random.randn(*(x1.shape))
                F, mask = cv2.findFundamentalMat(xx1, xx2, cv2.USAC_MAGSAC)
                mask = mask.ravel().astype(np.bool)

                df = df.append({'f_1 Prior': str(f_1_prior), 'f_1': ours_uncal(eng, F, f_1_prior, f2)[0], 'Method': 'Ours'}, ignore_index = True)
                df = df.append({'f_1 Prior': str(f_1_prior), 'f_1': hartley(F, xx1[mask], xx2[mask], f_1_prior, f2)[0] , 'Method': 'Hartley'}, ignore_index = True)
                df = df.append({'f_1 Prior': str(f_1_prior), 'f_1': fetzer_focal_only(F, f_1_prior, f2)[0] , 'Method': 'Fetzer'}, ignore_index = True)

                if f_1_prior == 600:
                    df = df.append({'f_1 Prior': 'No Prior', 'f_1': np.sqrt(bougnoux_original(F)[0]) , 'Method': 'Bougnoux'}, ignore_index = True)

        df.to_pickle(path)

    order = [str(x) for x in priors]
    order.append('No Prior')
    # sns.boxplot(data=df, x='f_1 Prior', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    custom_dodge_boxplot(data=df, x='f_1 Prior', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    plt.ylim(ylim)
    axes = plt.gca()
    xlim = (-0.5, len(order) - 0.5)
    plt.xlim(xlim)
    plt.legend(loc='upper left')
    l_gt, = plt.plot(xlim, [f1, f1], 'k--')
    plt.xlabel('$f_1$ Prior')
    plt.ylabel('Estimated $f_1$')
    plt.tick_params(bottom = False)

    legend_1 = axes.get_legend()

    for x, prior in enumerate(priors):
        l_prior, = plt.plot([x - 0.5, x + 0.5], [prior, prior], linestyle='--', color='0.8', zorder=2.0)
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25, zorder=2.0)

    handles = [l_gt, l_prior]
    labels = ['GT $f_1$', 'Prior $f_1$']
    axes.legend(handles, labels, loc='upper right')

    if legend_visible:
        axes.add_artist(legend_1)
    else:
        axes.get_legend().remove()


def uncal_weight_boxplot(load=True, ylim=(0, 1400), repeats=20, legend_visible=True):
    df = pd.DataFrame(columns = ['Weight', 'f_1', 'Method'])

    path = 'saved/synth/uncal_weights.pkl'

    eng = matlab.engine.start_matlab()
    s = eng.genpath('matlab_utils')
    eng.addpath(s, nargout=0)

    weights = [1e-5, 1e-4, 5e-4, 1e-3, 1e-2, 0.1, 1.0]

    sigma = 1.0

    thetas = np.random.rand(repeats) * 30 - 15
    ys = np.random.rand(repeats) * 400 - 200
    # thetas = np.random.randn(repeats) * 10.0
    # ys = np.random.randn(repeats) * 200

    f1 = 600
    f_1_prior = 1200
    f2 = 400

    scenes = [set_scene(f1, f2, theta=theta, y=y) for theta, y in zip(thetas, ys)]
    xs = [get_scene(*scene, 100, sigma_p=10) for scene in scenes]

    if load:
        df = pd.read_pickle(path)
    else:
        for weight in tqdm(weights):
            for x1, x2, _ in xs:
                xx1 = x1 + sigma * np.random.randn(*(x1.shape))
                xx2 = x2 + sigma * np.random.randn(*(x1.shape))
                F, mask = cv2.findFundamentalMat(xx1, xx2, cv2.USAC_MAGSAC)
                mask = mask.ravel().astype(np.bool)

                df = df.append({'Weight': str(weight), 'f_1': ours_uncal(eng, F, f_1_prior, f2, w1=weight, w3=weight)[0], 'Method': 'Ours'}, ignore_index = True)
                df = df.append({'Weight': str(weight), 'f_1': hartley(F, xx1[mask], xx2[mask], f_1_prior, f2, w_focal=0.0001*weight)[0], 'Method': 'Hartley'}, ignore_index = True)

                # if f_1_prior == 600:
                #     df = df.append({'f_1 Prior': 'No Prior', 'f_1': np.sqrt(bougnoux_original(F)[0]) , 'Method': 'Bougnoux'}, ignore_index = True)

        df.to_pickle(path)

    order = [str(x) for x in weights]
    custom_dodge_boxplot(data=df, x='Weight', y='f_1', hue='Method', dodge=True, order=order, width=0.8)
    plt.ylim(ylim)
    axes = plt.gca()
    xlim = (-0.5, len(order) - 0.5)
    plt.xlim(xlim)
    plt.legend(loc='upper left')
    l_gt, = plt.plot(xlim, [f1, f1], 'k--')
    plt.xlabel('$w_f/w_p$')
    plt.ylabel('Estimated $f_1$')
    plt.tick_params(bottom = False)

    legend_1 = axes.get_legend()

    for x, prior in enumerate(weights):
        l_prior, = plt.plot([x - 0.5, x + 0.5], [f_1_prior, f_1_prior], linestyle='--', color='0.8', zorder=2.0)
        plt.axvline(x + 0.5, color='0.5', linestyle='-', linewidth=0.25, zorder=2.0)

    handles = [l_gt, l_prior]
    labels = ['GT $f_1$', 'Prior $f_1$']
    axes.legend(handles, labels, loc='upper right')

    if legend_visible:
        axes.add_artist(legend_1)
    else:
        axes.get_legend().remove()

if __name__ == '__main__':
    load = False
    repeats = 100
    legend_visible = False
    figsize = (0.9*6, 0.9*4)

    plt.figure(figsize=figsize)
    uncal_coplanarity_y_plot(load=load, ylim=(0, 1400), repeats=repeats, legend_visible=legend_visible)
    plt.tight_layout()
    plt.savefig('figs/synth/uncal_coplanarity_y.pdf')

    plt.figure(figsize=figsize)
    uncal_coplanarity_plot(load=load, ylim=(0, 1400), repeats=repeats, legend_visible=legend_visible)
    plt.tight_layout()
    plt.savefig('figs/synth/uncal_coplanarity.pdf')

    # plt.figure(figsize=figsize)
    # uncal_noise_box_plot(load=load, ylim=(000, 1400), repeats=repeats, legend_visible=legend_visible)
    # plt.tight_layout()
    # plt.savefig('figs/synth/uncal_noise.pdf')
    #
    # plt.figure(figsize=figsize)
    # uncal_prior_boxplot(load=load, ylim=(000, 1400), repeats=repeats, legend_visible=legend_visible)
    # plt.tight_layout()
    # plt.savefig('figs/synth/uncal_prior.pdf')
    #
    # plt.figure(figsize=figsize)
    # uncal_principal_boxplot(load=load, repeats=repeats, legend_visible=legend_visible)
    # plt.tight_layout()
    # plt.savefig('figs/synth/uncal_principal.pdf')
    #
    # plt.figure(figsize=figsize)
    # uncal_weight_boxplot(load=load, repeats=repeats, ylim=(0, 1400), legend_visible=legend_visible)
    # plt.tight_layout()
    # plt.savefig('figs/synth/uncal_weights.pdf')
