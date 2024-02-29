import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
import matplotlib.pyplot as plt
import os
import plotly.graph_objects as go
st.set_page_config(page_title ="CAPM", page_icon = "chart_with_upwards_trend", layout = "wide")

#st.title("Relative Strength Model")

excel_pathF = "Stock_Futures.csv"
excel_pathN = "Equity_NSE.csv"
excel_pathB = "Only_BSE_Stocks.xlsx"

df_Fut = pd.read_csv(excel_pathF)
df_NSE = pd.read_csv(excel_pathN)
#df_BSE = pd.read_excel(excel_pathB)


options = ['FUTURES','NSE','BSE','Portfolio']

end_date=str(date.today())
month=int(end_date[5:7])
year=int(end_date[0:4])
year-=1
month-=1
# Create a select menu
selected_option = st.sidebar.selectbox("", options)
column1,column3,column2,column4 = st.columns([1,1,1,1])

options1 = ['d3','d5','d8','d13','d21','d34','d55','d89','d144']
options2 = ['d3','d5','d8','d13','d21','d34','d55','d89','d144','NA']
data=st.number_input("",value=21)
sort_opt1=['ASCENDING','DESCENDING']
sort_opt2=['ASCENDING','DESCENDING','NA']
with column1:
    Range1 = st.selectbox("", options1)
with column2:
    Range2 = st.selectbox("", options2)
with column3:
    Range3 = st.selectbox("", sort_opt1)
with column4:
    Range4 = st.selectbox("", sort_opt2)
    
def calculate(prod,stock_data):
    start_date=str(year)+"-"+str(month)+"-"+end_date[-2:]
    close_df=pd.DataFrame()
    volume_df=pd.DataFrame()
    for stock in stock_data:
        try:
            data=yf.download(stock+'.NS',start=start_date,end=end_date)
        except:
            print(stock)
        close_data = data['Close'].rename(stock)
        volume_data = data['Volume'].rename(stock)
        close_df = pd.concat([close_df, close_data], axis=1)
        volume_df = pd.concat([volume_df, volume_data], axis=1)
    close_df.reset_index(inplace=True)
    volume_df.reset_index(inplace=True)
    excel_path = prod+end_date+".xlsx"
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        close_df.to_excel(writer,sheet_name='close',index=False)
        volume_df.to_excel(writer, sheet_name='volume', index=False)

def display_data(df1,df2):
    df1['index'] = pd.to_datetime(df1['index'])
    df1.set_index('index', inplace=True)
    periods = [3, 5, 8, 13, 21, 34, 55, 89, 144]
    calculation_results = {}
    for period in periods:
        calculation = round(((df1.iloc[-1] - df1.iloc[-period]) / df1.iloc[-period]) * 100, 2)
        calculation_results[f'd{period}'] = calculation
    calculation_results['Stock'] = df1.columns
    calculation_df = pd.DataFrame(calculation_results)
    calculation_df.set_index('Stock', inplace=True)
    calculation_df.reset_index(inplace=True)
    stock_list1 = [[row[Range1],row['Stock']] for index, row in calculation_df.iterrows()]
    stock_list2 = [[row[Range2],row['Stock']] for index, row in calculation_df.iterrows()]
    if Range3=="ASCENDING":
        stock_list1.sort()
    else:
        stock_list1.sort(reverse=True)
    if Range4=="ASCENDING":
        stock_list2.sort()
    elif Range4=="DESCENDING":
        stock_list2.sort(reverse=True)
    else:
        st.write("NA")
    df3 = pd.DataFrame(stock_list1, columns=['Range1', 'Stock'])
    df4 = pd.DataFrame(stock_list2, columns=['Range2', 'Stock'])



    number_of_stock=st.sidebar.number_input("Enter the Number of Stock",step=1,value=10)
    df5=df3.head(number_of_stock)
    df6=df4.head(number_of_stock)
    combined_df = pd.merge(df5, df6, on='Stock', how='inner')
    combined_df2=combined_df.head(number_of_stock)
    def format_value(value):
        return "{:+07.2f}".format(value)
    combined_df2[['Range1', 'Range2']] = combined_df2[['Range1', 'Range2']].applymap(format_value)
    combined_df2['stock_change']=combined_df2['Stock']+'['+combined_df2['Range1']+']['+combined_df2['Range2']+']'
    #st.write(df1,df2)
    selected_option=st.sidebar.radio('',combined_df2['stock_change'])
    selected_option=selected_option[:-18]
    #chart_data.set_index('Date', inplace=True)
    chart_data = pd.DataFrame()
    chart_data2= pd.DataFrame()
# Iterate over each stock name and extract data from df_data
    for stock_name in combined_df2['Stock']:
    # Select data for the current stock and add it as a column to df_stocks_data
        chart_data[stock_name] = df1[stock_name]
        chart_data2[stock_name] = df2[stock_name]
    chart_data=chart_data.iloc[-data:]
    chart_data2=chart_data2.iloc[-data:]
    #st.write(chart_data,chart_data2)
        # Create a figure and axis object
    fig, ax1 = plt.subplots(figsize=(15, 8))

    # Plot the series on the primary axis
    ax1.fill_between(chart_data.index, chart_data[selected_option], alpha=0.2, color='tab:blue', label=selected_option)
    ax1.plot(chart_data.index, chart_data[selected_option], color='tab:blue', linewidth=2)

    # Set labels and ticks for the primary axis
    ax1.set_ylabel(selected_option, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_facecolor('#0E1117')
    ax1.xaxis.label.set_color('white')
    ax1.tick_params(axis='x', colors='white', rotation=45)
    ax1.set_ylim(min(chart_data[selected_option]), max(chart_data[selected_option]))
    ax2 = ax1.twinx()
    ax2.set_ylim(min(chart_data2[selected_option]),max(chart_data2[selected_option]))
    ax2.fill_between(chart_data.index, chart_data2[selected_option], alpha=0.01, color='#CC5500', label=selected_option)
    ax2.plot(chart_data.index, chart_data2[selected_option], color='#CC5500', linewidth=2)
    ax2.set_ylabel(selected_option, color='#CC5500')
    ax2.tick_params(axis='y', labelcolor='#CC5500')
    ax2.set_facecolor('#0E1117')  # Set inner chart background color
    fig.patch.set_facecolor('#0E1117')
    st.pyplot(fig)
    
if(selected_option=='FUTURES'):
    if(os.path.isfile(selected_option+end_date+'.xlsx')):
        close_df=pd.read_excel(selected_option+end_date+'.xlsx',sheet_name='close')
        volume_df=pd.read_excel(selected_option+end_date+'.xlsx',sheet_name='volume')
        display_data(close_df,volume_df)
    else:
        calculate(selected_option,df_Fut['Symbol'])

elif(selected_option=='NSE'):
    if(os.path.isfile(selected_option+end_date+'.xlsx')):
        close_df=pd.read_excel(selected_option+end_date+'.xlsx',sheet_name='close')
        volume_df=pd.read_excel(selected_option+end_date+'.xlsx',sheet_name='volume')
        display_data(close_df,volume_df)
    else:
        calculate(selected_option,df_Fut['Symbol'])
    
elif(selected_option=='BSE'):
    if(os.path.isfile(selected_option+end_date+'.xlsx')):
        close_df=pd.read_excel(selected_option+end_date+'.xlsx',sheet_name='close')
        volume_df=pd.read_excel(selected_option+end_date+'.xlsx',sheet_name='volume')
        display_data(close_df,volume_df)
    else:
        calculate(selected_option,df_Fut['Symbol'])

else:
    st.write("Select An Option")
    

