import streamlit as st
import pandas as pd
import finnhub

from datetime import date
import plotly.graph_objects as go

# Setup client
finnhub_client = finnhub.Client(api_key="cigl2m1r01qsmg0cmkogcigl2m1r01qsmg0cmkp0")

def daily_data(Symbol, date_start, date_end):
    # converting date to int format
    start_timestamp = pd.Timestamp(date_start).timestamp()
    end_timestamp = pd.Timestamp(date_end).timestamp()
    start_date = int(start_timestamp)
    end_date = int(end_timestamp)

    # reading it into dataframe
    Data = pd.DataFrame(finnhub_client.stock_candles(Symbol, "D", start_date, end_date))
    Data = Data[['c', 'h', 'l', 'o', 't', 'v']]
    Data.columns = ['Close', 'High', 'Low', 'Open', 'Date', 'Volume']
    Data['Date'] = Data['Date'].map(lambda x: pd.to_datetime(x, unit='s').date())
    Data['Symbol'] = Symbol
    Data = Data[['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return Data

def main():
    st.title("Stock Investment Returns Visualization")

    # User input
    Symbol = st.text_input("Enter Stock Symbol (e.g., MSFT)", "MSFT")
    initial_investment = st.number_input("Enter Initial Investment in $", min_value=1.0, value=1000.0, step=10.0)
    date_start = st.date_input("Enter Start Date", date(2015, 1, 1))
    date_end = st.date_input("Enter End Date", date.today())

    # Calling the function to get data
    Data = daily_data(Symbol, str(date_start), str(date_end))

    # Normalized closing price of share by dividing each day's price with the first price or starting price
    Norm = Data[['Date', 'Close']]
    Norm['Normalised'] = Data['Close'].div(Data['Close'].iloc[0]).mul(initial_investment)

    # Plotly line plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Norm['Date'], y=Norm['Normalised'], mode='lines', name='Investment Value'))
    fig.update_layout(title='Investment Value Over Time', xaxis_title='Date', yaxis_title='Investment Value')

    # Set x-axis range
    fig.update_xaxes(range=[Norm['Date'].min(), Norm['Date'].max()])

    # Set y-axis range to start from 0 and include the maximum investment value
    max_investment_value = Norm['Normalised'].max()
    fig.update_yaxes(range=[0, max_investment_value * 1.1])  # Adjust 1.1 to control the upper limit of y-axis

    # Display the chart
    st.plotly_chart(fig)

    # Calculate and display the final investment value
    final_investment_value = Norm.iloc[-1]['Normalised']
    st.success(f"Initial Investment Value: {initial_investment:.2f}")
    st.success(f"Final Investment Value: {final_investment_value:.2f}")
    st.success(f"Total return on investment is: {((final_investment_value-initial_investment)/initial_investment*100).round(2)} %")

if __name__ == "__main__":
    main()
