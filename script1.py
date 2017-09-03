from flask import Flask, render_template,request

app=Flask(__name__)

@app.route('/plot/',methods =['POST'])
def plot():
    from pandas_datareader import data
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2015,11,1)
    end = datetime.datetime.today().strftime("%Y/%m/%d")
    word = request.form['company_ip']

    df=data.DataReader(name=word,data_source="google",start=start,end=end)


    def inc_dec(c, o):
        if c > o:
            value="Increase"
        elif c < o:
            value="Decrease"
        else:
            value="Equal"
        return value

    df["Status"]=[inc_dec(c,o) for c, o in zip(df.Close,df.Open)]
    df["Middle"]=(df.Open+df.Close)/2
    df["Height"]=abs(df.Close-df.Open)

    p=figure(x_axis_type='datetime', width=1000, height=300, responsive=True)
    p.title.text="Candlestick Chart"
    p.grid.grid_line_alpha=0.3

    hours_12=12*60*60*1000

    p.segment(df.index, df.High, df.index, df.Low, color="Black")

    p.rect(df.index[df.Status=="Increase"],df.Middle[df.Status=="Increase"],
           hours_12, df.Height[df.Status=="Increase"],fill_color="#CCFFFF",line_color="black")

    p.rect(df.index[df.Status=="Decrease"],df.Middle[df.Status=="Decrease"],
           hours_12, df.Height[df.Status=="Decrease"],fill_color="#FF3333",line_color="black")

    script1, div1 = components(p)
    cdn_js=CDN.js_files[0]
    cdn_css=CDN.css_files[0]
    predicted = predict_prices(df.Middle[-10:],29)
    print(predicted)
    return render_template("plot.html",
    script1=script1,
    predicted = predicted,
    div1=div1,
    cdn_css=cdn_css,
    cdn_js=cdn_js )
    

    
def predict_prices(prices,x):
    from sklearn.svm import SVR
    import numpy as np
    
    dates = list(range(len(prices)))
    dates = np.reshape(dates,(len(dates),1))
    svr_rbf = SVR(kernel = 'rbf',C=1e3,gamma=0.1)
    svr_rbf.fit(dates,prices)

    return svr_rbf.predict(x)[0]


@app.route('/')
def home():
    return render_template("index.html")


if __name__=="__main__":
    app.run(debug=True)
