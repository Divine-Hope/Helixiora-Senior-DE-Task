import requests
import pandas as pd
import matplotlib.pyplot as plt


def fetch_exchange_rates(url):
    response = requests.get(url=url)
    return pd.DataFrame(response.json())


def preprocess_data(df):
    df['date'] = pd.to_datetime(df['date'])
    years = ['2022', '2023', '2024']
    filtered_data = {}
    for year in years:
        start_date = pd.to_datetime(f'{year}-01-01')
        end_date = pd.to_datetime(f'{year}-12-31') if year != '2024' else df['date'].max()
        filtered_data[year] = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return filtered_data


def calculate_statistics(filtered_data):
    statistics = {}
    for year, data in filtered_data.items():
        statistics[f'avg_rates_{year}'] = data.select_dtypes(include=['float64', 'int']).mean()
    percent_changes = {
        '2022-2023': ((statistics['avg_rates_2023'] - statistics['avg_rates_2022']) / statistics[
            'avg_rates_2022']) * 100,
        '2023-2024': ((statistics['avg_rates_2024'] - statistics['avg_rates_2023']) / statistics[
            'avg_rates_2023']) * 100,
    }
    return percent_changes


def add_value_labels(ax, spacing=5):
    for rect in ax.patches:
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2
        space = -spacing if y_value < 0 else spacing
        va = 'bottom' if y_value >= 0 else 'top'
        label = "{:.1f}%".format(y_value)
        ax.annotate(label, (x_value, y_value), xytext=(0, space), textcoords="offset points", ha='center', va=va)


def plot_data(exchange_rates, percent_changes):
    for period, changes in percent_changes.items():
        _, ax = plt.subplots(figsize=(10, 6))
        ax.bar(changes.index.str.replace('myr_', '').str.upper(), changes.values)
        ax.set_title(f'Percent Change {period}')
        ax.tick_params(axis='x', rotation=90)
        ax.set_ylabel('Percent Change (%)')
        add_value_labels(ax, spacing=10)
        plt.show()

    # Plot trend over time for selected currencies
    data_monthly_avg = exchange_rates.set_index('date').resample('ME').mean()
    currency_columns = [col for col in data_monthly_avg.columns if col != 'date']
    selected_currencies = [currency for currency in currency_columns if currency not in ('myr_vnd', 'myr_idr', 'myr_krw')]
    plt.figure(figsize=(10, 6))
    data_monthly_avg = exchange_rates.set_index('date').resample('ME').mean()
    data_monthly_avg[selected_currencies].plot(title='Trend Over Time (2022-2024)')
    plt.ylabel('Exchange Rate')
    plt.legend([currency.upper().replace('MYR_', '') for currency in selected_currencies])
    # plt.ylim(0, 1000)
    plt.show()

    # Plot consolidated percent change for 2022-2024
    plt.figure(figsize=(10, 6))
    pd.DataFrame(percent_changes).plot.bar()
    plt.title('Consolidated Percent Change 2022-2024')
    plt.xticks(rotation=90)
    plt.ylabel('Percent Change (%)')
    plt.show()


def main():
    url = "https://api.data.gov.my/data-catalogue?id=exchangerates"
    exchange_rates = fetch_exchange_rates(url)
    filtered_data = preprocess_data(exchange_rates)
    percent_changes = calculate_statistics(filtered_data)
    plot_data(exchange_rates, percent_changes)


if __name__ == "__main__":
    main()
