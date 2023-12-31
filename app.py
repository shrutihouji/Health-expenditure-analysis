from flask import Flask, render_template,request,redirect
import plotly.express as px
import pandas as pd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

app=Flask(__name__)

df=pd.read_csv('filtered_data.csv')

def get_yearwise_value_pp(df):
  years = df.year.unique()
  yearwise_sum = []
  for year in years:
    yearwise_sum.append(df.loc[df['year'] == year, 'purchasing power parity'].sum())
  return years, yearwise_sum

def get_yearwise_value_er(df):
  years = df.year.unique()
  yearwise_sum = []
  for year in years:
    yearwise_sum.append(df.loc[df['year'] == year, 'exchange rates'].sum())
  return years, yearwise_sum

def get_yearwise_value_op(df):
  years = df.year.unique()
  yearwise_sum = []
  for year in years:
    yearwise_sum.append(df.loc[df['year'] == year, 'out-of-pocket expenses'].sum())
  return years, yearwise_sum

@app.route('/',methods=['GET','POST'])
def time_series_plot():

    plot_area = None
    #line plot
    df.rename(columns={'che_pc_usd':'current healthcare expenditure(USD)'},inplace=True)
    df['current healthcare expenditure(USD)'].isnull().sum()
    df_che=df[['country','year','income','current healthcare expenditure(USD)']].copy()
    df_che=df_che.round(2)
    df_che.dropna(subset=['current healthcare expenditure(USD)'],inplace=True)

    if request.method == 'POST':
        selected_year = request.form['year']
        df_selected = df_che[df_che['year'] == int(selected_year)]

        df_selected_top10 = df_selected.nlargest(10, 'current healthcare expenditure(USD)')
        fig_bar = px.line(df_selected_top10, x='country', y='current healthcare expenditure(USD)', title='Top 10 countries with current healthcare expenditure per capita(in USD)'
                 )
        fig_bar.update_layout(
            xaxis=dict(tickangle=45),
            xaxis_title='Country',
            yaxis_title='healthcare expenditure per capita',
            xaxis_categoryorder='total descending'
        
        )
        fig_bar.add_trace(px.scatter(df_selected_top10, x='country', y='current healthcare expenditure(USD)',
                                 color_discrete_sequence=['red']).data[0])
        plot_area = fig_bar.to_html(full_html=False)
      


    #bar plot
    #plot 8
    df.rename(columns={'pop':'Population'},inplace=True)
    df_usa = df[df['country'] == 'United States of America']

    fig_n = px.bar(df_usa, x='year', y=['Population', 'current healthcare expenditure(USD)'],
             barmode='group',
             title='Realtionship between Population(in Thousands) and Current Healthcare Expenditure per Capita',
             labels={'value': 'Amount'},
             height=500,
             color_discrete_map={'Population': '#003366', 'current healthcare expenditure(USD)': '#FFA500'})
    plot_html_n=fig_n.to_html(full_html=False)
    
    #sunburst chart
    region_mapping = {
    'AFR': 'Africa',
    'AMR': 'America',
    'EUR': 'Europe',
    'EMR': 'Eastern Mediterranean',
    'WPR': 'Western Pacific',
    'SEAR': 'South-East Asia'
}
    region_colors = {
    'Africa': '#EC7063',   
    'America': '#AF7AC5',  
    'Eastern Mediterranean': '#48C9B0',  
    'Europe': '#7FB3D5',   
    'South-East Asia': '#F9E79F',  
    'Western Pacific': '#F5B7B1'   
}
    df['region'] = df['region'].replace(region_mapping)
    # Filter data for the year 2010
    df_10 = df[df['year'] == 2010]

    fig = px.sunburst(df_10, path=['region','income','country'], values='che_gdp',color='region',color_discrete_map=region_colors,
                    title='2010 Health Expenditure as % of GDP Across Income Groups')


    plot_html=fig.to_html(full_html=False)
    # Filter data for the year 2020
    df_20 = df[df['year'] == 2020]

    fig1 = px.sunburst(df_20, path=['region','income','country'], values='che_gdp',color='region',color_discrete_map=region_colors,
                    title='2020 Health Expenditure as % of GDP Across Income Groups')


    plot_html1=fig1.to_html(full_html=False)

    #Tree map
    selected_columns = ['country', 'hf_usd', 'hf1_usd', 'hf11_usd', 'hf2_usd', 'hf21_usd', 'hf22_usd', 'hf3_usd']
    data_health_exp = df[selected_columns]
    #melt the DataFrame to long format 
    melted_data = pd.melt(data_health_exp, id_vars='country', var_name='financing_source', value_name='expenditure')

    #convert 'expenditure' column to numerical type and handle NaN values
    melted_data['expenditure'] = pd.to_numeric(melted_data['expenditure'], errors='coerce')

    #remove negative or zero values
    melted_data = melted_data[melted_data['expenditure'] > 0]

    #replace financing source names with custom labels
    financing_source_labels = {
        'hf_usd': 'Total Health Expenditure',
        'hf1_usd': 'Government Schemes & Compulsory Contributions',
        'hf11_usd': 'Government Schemes',
        'hf2_usd': 'Voluntary Health Payment Schemes',
        'hf21_usd': 'Voluntary Health Insurance Schemes',
        'hf22_usd': 'NPISH Financing Schemes (including development agencies)',
        'hf3_usd': 'Household Out-of-Pocket Payment',
    }
    melted_data['financing_source'] = melted_data['financing_source'].map(financing_source_labels)
    fig3 = px.treemap(melted_data.dropna(), 
                    path=['country', 'financing_source'],
                    values='expenditure',
                    color='expenditure',
                    color_continuous_scale='Viridis',
                    color_continuous_midpoint=melted_data['expenditure'].mean(),
                    hover_data={'expenditure': True, 'financing_source': True, 'country': False},
                    title='Heathcare expenditure for different categories of financing schemes(in millions USD)'
                    )
    fig3.update_traces(textinfo='label+value+percent entry')  
    plot_html2=fig3.to_html(full_html=False)

    #time series plot
    health_df = pd.DataFrame(df)
    health_df['che_gdp'] = pd.to_numeric(health_df['che_gdp'], errors='coerce')
    health_df = health_df.dropna(subset=['che_gdp'])
    avg_che_gdp_data = health_df.groupby(['year', 'region']).agg({'che_gdp': 'mean'}).reset_index()
    avg_che_gdp_data['che_gdp_smoothed'] = avg_che_gdp_data.groupby('region')['che_gdp'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
    fig5 = px.line(avg_che_gdp_data, x='year', y='che_gdp_smoothed', color='region',
                line_shape='linear',  # You can change the line shape as needed
                title='Smoothed Current Health Expenditure as % GDP Over Time for Each Region')
    fig5.update_layout(
        xaxis_title='Year',
        yaxis_title='Smoothed Current Health Expenditure as % of GDP',
        legend_title='Region',
    )
    plot_html4=fig5.to_html(full_html=False)

    #heatmap
    fig5_new = px.imshow(avg_che_gdp_data.pivot_table(index='region', columns='year', values='che_gdp'),
                x=list(avg_che_gdp_data['year'].unique()),
                y=list(avg_che_gdp_data['region'].unique()),
                title='Heatmap of Current Health Expenditure as % GDP by Region and Year',
                color_continuous_scale='YlGnBu',
                labels={'color': 'che as % GDP'})
    plot_html4_2=fig5_new.to_html(full_html=False)

    #plot 6 
    df.rename(columns={'gghed_che':'Domestic General Government Health Expenditure(GGHE-D) as %(CHE)'},inplace=True)
    df.rename(columns={'pvtd_che':'Domestic Private Health Expenditure (PVT-D) as %(CHE)'},inplace=True)
    df.rename(columns={'che_pc_usd':'current healthcare expenditure(USD)'},inplace=True)
    data_for_2020 = df[df['year'] == 2010]
    fig6 = px.scatter(data_for_2020,
                 x='Domestic General Government Health Expenditure(GGHE-D) as %(CHE)',
                 y='Domestic Private Health Expenditure (PVT-D) as %(CHE)',
                 size='current healthcare expenditure(USD)',  #size of bubble
                 color='Domestic General Government Health Expenditure(GGHE-D) as %(CHE)',  #color based on the government expenditure percentage
                 hover_name='country',  #display country name on hover
                 labels={'Domestic General Government Health Expenditure(GGHE-D) as %(CHE)': 'Government Health Expenditure %', 'Domestic Private Health Expenditure (PVT-D) as %(CHE)': 'Private Health Expenditure %'},
                 title='Healthcare Financing by Government and Private Sources',
                 size_max=60)

    fig6.update_layout(xaxis_title='Government Health Expenditure %',
                  yaxis_title='Private Health Expenditure %',
                  coloraxis_colorbar=dict(title='Government Health Expenditure%'))

    plot_html5=fig6.to_html(full_html=False)


    #plot 7- dot map plot
    df.rename(columns={'hf11_usd_pc':'Govn_schemes_USD_PC'},inplace=True)
    usd=df[['country','year','code','income','Govn_schemes_USD_PC']]
    usd=usd.round(2)
    fig7 = px.scatter_geo(usd,
                     locations='code',  
                     size='Govn_schemes_USD_PC', 
                     color='income', 
                     hover_name='country',  
                     hover_data=['Govn_schemes_USD_PC'],  
                     title='Government Spending on Schemes in USD Per Capita by Country and Income Group',
                     projection='natural earth',
                     animation_frame='year',  # creates a slider based on the 'year' column
                     size_max=30,
                     color_discrete_sequence=px.colors.qualitative.Plotly) 
    #setting minimum size 
    fig7.update_traces(marker=dict(sizemin=3))

    fig7.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
        )
    )
    fig7.update_traces(marker=dict(line=dict(width=0)))
    plot_html6=fig7.to_html(full_html=False)

    #spider chart
    spider_data = ['year', 'ppp', 'xrt', 'oops_che', 'region']
    data_spider_chart = df[spider_data]
    #renaming for income level per capita
    data_spider_chart.rename(columns={'ppp':'purchasing power parity'},inplace=True)
    #renaming for  highest healthcare expenditure
    data_spider_chart.rename(columns={'xrt':'exchange rates'},inplace=True)
    #renaming for total current healthcare expenditure
    data_spider_chart.rename(columns={'oops_che':'out-of-pocket expenses'},inplace=True)

    years_pp, yearwise_ppp = get_yearwise_value_pp(data_spider_chart)
    years_er, yearwise_xrt = get_yearwise_value_er(data_spider_chart)
    years_op, yearwise_oops_che = get_yearwise_value_op(data_spider_chart)

    years_pp = [*years_pp, years_pp[0]]
    yearwise_ppp = [*yearwise_ppp, yearwise_ppp[0]]
    yearwise_xrt = [*yearwise_xrt, yearwise_xrt[0]]

    fig8 = go.Figure(
        data=[
            go.Scatterpolar(r=yearwise_ppp, theta=[str(year) for year in years_pp], name='purchasing power parity'),
            go.Scatterpolar(r=yearwise_xrt, theta=[str(year) for year in years_er], name='exchange rates'),
        ],
        layout=go.Layout(
            title=go.layout.Title(text='Purchasing Power Parity and Exchange Rate (NCU per US$)'),
            polar={'radialaxis': {'visible': True}},
            showlegend=True
        )
    )
    plot_html7=fig8.to_html(full_html=False)

    return render_template('index2.html',plot=plot_area,plot_bar=plot_html_n,plot1=plot_html,plot2=plot_html1,plot3=plot_html2,plot5=plot_html4,  plot5_2=plot_html4_2, plot6=plot_html5, plot7=plot_html6, plot8=plot_html7)


if __name__ == '__main__':
    app.run(debug=True)
