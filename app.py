import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from plotly import graph_objs as go
from datetime import date


st.set_page_config(page_title="My App",layout='wide')
st.title('Trade Guru')

#pick a stock
selected_stock = st.text_input("Pick a stock", 'RELIANCE.NS' )
data = yf.download(tickers = selected_stock.upper(), Period="max")
data=data[::-1]
data=data.head(1000)
data=data[::-1]
data.to_pickle('Relpkl.pkl')
st.write("loaded data for", selected_stock)
st.dataframe(data)

#pick a strategy
strategy_pick = ('Select','EMA_CROSS','SUPERTREND')
selected_strat = st.selectbox('Select strategy', strategy_pick)

#declarations
trades = []
trades2 = []
date_buy = []
date_sell = []
date_buy2 = []
date_sell2 = []




#strat EMA_CROSS
if (selected_strat=='EMA_CROSS'):
    st.write("EMA")
    x = st.slider('EMA 1', 5,20,value=9)
    y = st.slider('EMA 2', 21,50,value=26)
    emaStrategy = ta.Strategy(name="EMA-Cross",description="EMA_Cross",ta=[{"kind": "ema", "length": x},{"kind": "ema", "length": y}])
    data.ta.strategy(emaStrategy)
    data['signal'] = np.where(data["EMA_{}".format(x)] > data["EMA_{}".format(y)], 1, 0)
    data['position'] = data['signal'].diff()
    
    trade = False
    t = 0
    bl=[]
    for i in range(0, len(data)):
        if (trade == False and data['position'][i] == 1):
            t = data['Close'][i]
            bl.append(data['Close'][i])
            date_buy.append(str(data.index[i].date()))
            trade = True
        if (trade == True and float(data['Close'][i]) <= float((0.95 * t))):
            profit = data['Close'][i] - t
            date_sell.append(str(data.index[i].date()))
            trades.append(profit)
            trade = False
        if (trade == True and data['position'][i] == -1):
            profit = data['Close'][i] - t
            date_sell.append(str(data.index[i].date()))
            trades.append(profit)
            trade = False

    
    
    #graph1
    chart_data = pd.DataFrame(data,columns=['EMA_{}'.format(y), 'EMA_{}'.format(x)])
    st.line_chart(chart_data,height=500,width=1000)
    data['buy'] = np.where(data['position'] == 1, data['Close'], np.NAN)
    data['sell'] = np.where(data['position'] == -1, data['Close'], np.NAN)
    
    
    #graph2
    def plot_raw_data():
        fig = go.Figure(data=[go.Candlestick(x=data.index,open=data['Open'],high=data['High'],low=data['Low'],close=data['Close'])])
        #fig.add_trace(go.Scatter(x=data.index, y=data['EMA_{}'.format(y)], name='EMA_{}'.format(y)))
        #fig.add_trace(go.Scatter(x=data.index, y=data['EMA_{}'.format(x)], name='EMA_{}'.format(x)))
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close',line=dict(color='black')))
        fig.add_trace(go.Scatter(x=data.index, y=data['buy'],mode='markers', name='Buy',marker = dict(size = 10, color = 'palegreen')))
        fig.add_trace(go.Scatter(x=data.index, y=data['sell'],mode='markers', name='Sell',marker = dict(size = 10, color = 'royalblue')))
        fig.layout.update(title_text='Graph with Rangeslider', xaxis_rangeslider_visible=True)
        fig.update_layout(width=1300,height=1000)
        st.plotly_chart(fig)
        
    plot_raw_data()
    
    #Display trades
    
    st.write("Number of Trades :",len(trades))
    tl=list(map(lambda x, y, z: x + '<---Buy_date__Trade__Sell_date---> ' +y +'  Diffrence  ' +str(z), date_buy, date_sell, trades ))
    ptl=[]
    ltl=[]
    for i in range(0,len(trades)):
        if (trades[i]>=0):
            ptl.append(tl[i])
        else:
            ltl.append(tl[i])
    st.write("Trade info", tl)
    st.write("Profit Trades",ptl)
    st.write("Loss Trades",ltl)
    st.write("trades profit :",trades)
    st.write("Net Profit :",sum(trades))
    
    
    #ROI Logic
    inv1 = int(st.text_input("Investment amount", '1000' ))
    inv=inv1
    for i in range(0,len(trades)):
        inv=inv+((inv/bl[i])*trades[i])
    st.write("Your investment would be now worth",inv)
    st.write("**ROI :  {} % **".format((inv/inv1)*100))
    
    
    
    
#Strat Supertrend
if (selected_strat=='SUPERTREND'):
    st.write("SUPERTREND")
    
    l = st.slider('Lookback', 1,20,value=10)
    m = st.slider('Multiplier',min_value=1.0,max_value=10.0,value=3.0,step=0.1)
    df2= ta.supertrend(data['High'],data['Low'],data['Close'],l,m)
    data['supertrendFlag']=df2['SUPERTd_{}_{}'.format(l,m)]
    data['position2']=data['supertrendFlag'].diff()
    data['buy2']= np.where(data['position2']==2 ,data['Close'],np.NAN)
    data['sell2']= np.where(data['position2']==-2,data['Close'],np.NAN)
    
    trade2= False
    
    #graph1
    chart_data = pd.DataFrame(data,columns=['Close'])
    st.line_chart(chart_data)
    
    #graph2
    def plot_raw_data():
        fig = go.Figure(data=[go.Candlestick(x=data.index,open=data['Open'],high=data['High'],low=data['Low'],close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close'))
        
        fig.add_trace(go.Scatter(x=data.index, y=data['buy2'],mode='markers', name='buy',marker = dict(size = 10, color = 'palegreen')))
        fig.add_trace(go.Scatter(x=data.index, y=data['sell2'],mode='markers', name='sell',marker = dict(size = 10, color = 'royalblue')))
        fig.layout.update(title_text='Graph with Rangeslider', xaxis_rangeslider_visible=True)
        fig.update_layout(width=1300,height=1000)
        st.plotly_chart(fig)

    plot_raw_data()
    
    t1=0
    profit=0
    bl2=[]
    for i in range(0,len(data)):
        if(trade2==False and data['position2'][i]==2):
            t1=data['Close'][i]
            bl2.append(data['Close'][i])
            date_buy2.append(str(data.index[i].date()))
            trade2=True
            
        if(trade2==True and float(data['Close'][i])<=float((0.95*t1))):
            profit=data['Close'][i]-t1
            trades2.append(profit)
            date_sell2.append(str(data.index[i].date()))
            trade2=False
        if(trade2==True and data['position2'][i]==-2):
            profit=data['Close'][i]-t1
            trades2.append(profit)
            date_sell2.append(str(data.index[i].date()))
            trade2=False
           
    start2=1.0
    
    
    
    #Display trades
    
    st.write("Number of Trades :",len(trades2))
    tl2=list(map(lambda x, y, z: x + '<---Buy_date__Trade__Sell_date---> ' +y +'  Diffrence  ' +str(z), date_buy2, date_sell2, trades2 ))
    ptl2=[]
    ltl2=[]
    for i in range(0,len(trades2)):
        if (trades2[i]>=0):
            ptl2.append(tl2[i])
        else:
            ltl2.append(tl2[i])
            
    

    st.write("Trade info", tl2)
    st.write("Profit Trades",ptl2)
    st.write("Loss Trades",ltl2)
    st.write("trades profit", trades2)
    st.write("Net Profit :",sum(trades2))
    
    
    #ROI Logic
    inv21 = int(st.text_input("Investment amount", '1000' ))
    inv2=inv21
    for i in range(0,len(trades2)):
        inv2=inv2+((inv2/bl2[i])*trades2[i])
    st.write("Your investment would be now worth",inv2)
    st.write("**ROI :  {} % **".format((inv2/inv21)*100))
