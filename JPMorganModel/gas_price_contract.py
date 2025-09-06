import pandas as pd

# === Step 1: Read CSV and prepare price_data dictionary ===
df = pd.read_csv("gas_prices.csv")
df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%y")  
price_data = dict(zip(df['Date'].dt.strftime('%Y-%m-%d'), df['Prices']))

# === Step 2: Define the pricing function (as before) ===
def price_gas_contract(
    injection_dates,
    withdrawal_dates,
    injection_volumes,
    withdrawal_volumes,
    price_data,
    injection_cost_per_mmbtu=0,
    withdrawal_cost_per_mmbtu=0,
    storage_cost_per_month=0,
    max_storage_volume=None
):
    price_data = {
        pd.to_datetime(k).strftime('%Y-%m-%d'): v
        for k, v in price_data.items()
    }

    if len(injection_dates) != len(injection_volumes) or len(withdrawal_dates) != len(withdrawal_volumes):
        return {"Error": "Date and volume lists don't match in length"}

    total_injected = sum(injection_volumes)
    total_withdrawn = sum(withdrawal_volumes)

    if total_injected != total_withdrawn:
        return {"Error": "Total injected and withdrawn volumes must match"}

    if max_storage_volume:
        for vol in injection_volumes:
            if vol > max_storage_volume:
                return {"Error": "Volume exceeds max storage capacity"}

    buy_cost = 0
    sell_revenue = 0
    storage_cost = 0

    for inj, vol, wd in zip(injection_dates, injection_volumes, withdrawal_dates):
        inj_date = pd.to_datetime(inj)
        wd_date = pd.to_datetime(wd)

        inj_key = inj_date.strftime('%Y-%m-%d')
        wd_key = wd_date.strftime('%Y-%m-%d')

        if inj_key not in price_data or wd_key not in price_data:
            return {"Error": f"Missing price for {inj_key} or {wd_key}"}

        buy_price = price_data[inj_key]
        sell_price = price_data[wd_key]

        buy_cost += buy_price * vol
        sell_revenue += sell_price * vol

        months = (wd_date - inj_date).days // 30
        storage_cost += months * storage_cost_per_month * vol

    inj_fee = total_injected * injection_cost_per_mmbtu
    wd_fee = total_withdrawn * withdrawal_cost_per_mmbtu

    net_value = sell_revenue - buy_cost - storage_cost - inj_fee - wd_fee

    return {
        "Buy Cost": round(buy_cost, 2),
        "Sell Revenue": round(sell_revenue, 2),
        "Storage Cost": round(storage_cost, 2),
        "Injection Cost": round(inj_fee, 2),
        "Withdrawal Cost": round(wd_fee, 2),
        "Net Value": round(net_value, 2)
    }

# === Step 3: Example contract test ===
result = price_gas_contract(
    injection_dates=["2022-10-31", "2022-11-30"],
    withdrawal_dates=["2023-03-31", "2023-04-30"],
    injection_volumes=[1000, 1500],
    withdrawal_volumes=[1000, 1500],
    price_data=price_data,
    injection_cost_per_mmbtu=0.1,
    withdrawal_cost_per_mmbtu=0.1,
    storage_cost_per_month=0.05,
    max_storage_volume=3000
)

print(result)
