

def plot_time_ranges(csv1, csv2, out_path):
    fig = plt.figure(figsize =(10, 7))
    axes = fig.add_subplot(111)
    plt.title("PPG Ground truth vs SensorKit", fontsize=14, fontweight="bold")

    axes.set_title('PPG', fontsize=12, fontweight="bold")
    axes.set_xlabel('CFAbsoluteTime', fontsize=12)
    axes.xaxis.set_major_formatter(
        plt.FuncFormatter(ios_time_formatter))
    plt.xticks(rotation=45)

    axes.set_ylabel('PPG', fontsize=12)
    axes.legend(loc="upper right")

    df1 = read_csv(csv1, names=[
        "startCFTime",
        "endCFTime",
        "count"])

    df2 = read_csv(csv2, names=[
        "startCFTime",
        "endCFTime",
        "count"])

    axes.scatter(
        df1["startCFTime"],
        df1["count"],
        color="green",
        s=3,
        label="z",
        marker='o')

    axes.scatter(
        df2["startCFTime"],
        df2["count"],
        color="red",
        s=3,
        label="z",
        marker='D')

    fig.savefig(out_path)
