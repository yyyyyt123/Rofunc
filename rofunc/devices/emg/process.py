import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np


def process(data, sampling_rate, k):
    """

    Args:
        data: raw emg data
        sampling_rate: recorded at samples / second
        k: filtering rate of data to samples / k / second


    Returns:
    data_filter: Filter the original EMG signals (from the Delsys system, 2000 Hz) to the desired frequency
    data_clean: Clean the raw EMG signals
    data_mvc: Calculate the Maximum Voluntary Contraction (MVC) of the EMG signals
    data_abs: Take the absolute value of the EMG signals
    """
    data_filter = []
    for i in range(0, len(data) - k + 1, k):
        data_new = data[i]
        data_filter.append(data_new)
    data_filter = np.array(data_filter)

    signals, info = nk.emg_process(data_filter, sampling_rate=sampling_rate)
    signals_array = signals.values
    data_clean = signals_array[:, 1]
    data_mvc = signals_array[:, 2]

    data_abs = [0] * len(data_clean)
    for i in range(len(data_clean)):
        data_abs[i] = abs(data_clean[i])
    data_abs = np.array(data_abs)
    return data_filter, data_clean, data_mvc, data_abs


def plot_raw_and_clean(data_filter, data_clean):
    fig, ax0 = plt.subplots(nrows=1, ncols=1, sharex=True)
    ax0.set_xlabel("Time (seconds)", fontweight="bold", fontdict={'family': 'Times New Roman'}, fontsize=12)
    fig.suptitle("Raw and Clean EMG Signals", fontweight="bold", fontdict={'family': 'Times New Roman'},
                 fontsize=16)
    plt.subplots_adjust(hspace=0.2)
    x_axis = np.linspace(0, data_filter.shape[0] / int(SAMPING_RATE / k), data_filter.shape[0])
    legend_font = {"family": "Times New Roman"}
    ax0.set_title("Sensor_1", fontdict={'family': 'Times New Roman'}, fontsize=12)
    ax0.plot(x_axis, data_filter, color="#B0BEC5", label="Raw", zorder=1)
    ax0.plot(
        x_axis, data_clean, color="#FFC107", label="Cleaned", zorder=1, linewidth=1.5
    )
    ax0.legend(loc="upper right", frameon=True, prop=legend_font)


def plot_abs_and_mvc(data_abs, data_mvc):
    fig, ax0 = plt.subplots(nrows=1, ncols=1, sharex=True)
    ax0.set_xlabel("Time (seconds)", fontweight="bold", fontdict={'family': 'Times New Roman'}, fontsize=12)
    fig.suptitle("Absolute Value and MVC of EMG signals", fontweight="bold",
                 fontdict={'family': 'Times New Roman'}, fontsize=16)
    plt.subplots_adjust(hspace=0.2)
    x_axis = np.linspace(0, data_abs.shape[0] / int(SAMPING_RATE / n), data_abs.shape[0])
    legend_font = {"family": "Times New Roman"}
    ax0.set_title("Sensor_1", fontdict={'family': 'Times New Roman'}, fontsize=12)
    ax0.plot(x_axis, data_abs, color="#B0BEC5", label="ABS", zorder=1)
    ax1 = ax0.twinx()
    ax1.plot(
        x_axis, data_mvc, color="#FA6839", label="MVC", linewidth=1.5
    )
    ax0.legend(loc="upper left", frameon=True, prop=legend_font)
    ax1.legend(loc="upper right", frameon=True, prop=legend_font)


if __name__ == '__main__':
    emg = np.load('./data/emg_data.npy')
    SAMPING_RATE = 2000
    k = 4
    n = 4
    data_filter = [0] * n
    data_clean = [0] * n
    data_mvc = [0] * n
    data_abs = [0] * n
    for i in range(n):
        data_filter[i], data_clean[i], data_mvc[i], data_abs[i] = process(emg[:, i], SAMPING_RATE, k)
        plot_raw_and_clean(data_filter[i], data_clean[i])
        plot_abs_and_mvc(data_abs[i], data_mvc[i])
    plt.show()

    # data_filter_1, data_clean_1, data_mvc_1, data_abs_1 = process(emg[:, 0], SAMPING_RATE, n)
    # data_filter_2, data_clean_2, data_mvc_2, data_abs_2 = process(emg[:, 1], SAMPING_RATE, n)

    # # Plot cleaned and raw EMG.
    # fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, sharex=True)
    # ax1.set_xlabel("Time (seconds)", fontweight="bold", fontdict={'family': 'Times New Roman'}, fontsize=12)
    # fig.suptitle("Raw and Clean EMG Signals", fontweight="bold", fontdict={'family': 'Times New Roman'},
    #              fontsize=16)
    # plt.subplots_adjust(hspace=0.2)
    # x_axis = np.linspace(0, data_filter_1.shape[0] / int(SAMPING_RATE / n), data_filter_1.shape[0])
    # legend_font = {"family": "Times New Roman"}
    # ax0.set_title("Sensor_1", fontdict={'family': 'Times New Roman'}, fontsize=12)
    # ax0.plot(x_axis, data_filter_1, color="#B0BEC5", label="Raw", zorder=1)
    # ax0.plot(
    #     x_axis, data_clean_1, color="#FFC107", label="Cleaned", zorder=1, linewidth=1.5
    # )
    # ax0.legend(loc="upper right", frameon=True, prop=legend_font)
    # ax1.set_title("Sensor_2", fontdict={'family': 'Times New Roman'}, fontsize=12)
    # ax1.plot(x_axis, data_filter_2, color="#B0BEC5", label="Raw", zorder=1)
    # ax1.plot(
    #     x_axis, data_clean_2, color="#FFC107", label="Cleaned", zorder=1, linewidth=1.5
    # )
    # ax1.legend(loc="upper right", frameon=True, prop=legend_font)
    # plt.show()
    #
    # # Plot absolute value and MVC of EMG.
    # fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, sharex=True)
    # ax1.set_xlabel("Time (seconds)", fontweight="bold", fontdict={'family': 'Times New Roman'}, fontsize=12)
    # fig.suptitle("Absolute Value and MVC of EMG signals", fontweight="bold",
    #              fontdict={'family': 'Times New Roman'}, fontsize=16)
    # plt.subplots_adjust(hspace=0.2)
    # x_axis = np.linspace(0, data_abs_1.shape[0] / int(SAMPING_RATE / n), data_abs_1.shape[0])
    # ax0.set_title("Sensor_1", fontdict={'family': 'Times New Roman'}, fontsize=12)
    # ax0.plot(x_axis, data_abs_1, color="#B0BEC5", label="ABS", zorder=1)
    # ax2 = ax0.twinx()
    # ax2.plot(
    #     x_axis, data_mvc_1, color="#FA6839", label="MVC", linewidth=1.5
    # )
    # ax0.legend(loc="upper left", frameon=True, prop=legend_font)
    # ax2.legend(loc="upper right", frameon=True, prop=legend_font)
    # ax1.set_title("Sensor_2", fontdict={'family': 'Times New Roman'}, fontsize=12)
    # ax1.plot(x_axis, data_abs_2, color="#B0BEC5", label="ABS", zorder=1)
    # ax3 = ax1.twinx()
    # ax3.plot(
    #     x_axis, data_mvc_2, color="#FA6839", label="MVC", linewidth=1.5
    # )
    # ax1.legend(loc="upper left", frameon=True, prop=legend_font)
    # ax3.legend(loc="upper right", frameon=True, prop=legend_font)
    # plt.show()
