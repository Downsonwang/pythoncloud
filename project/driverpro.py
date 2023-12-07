
import os
import tkinter as tk
import webbrowser
from pymongo import MongoClient
from tkinter import messagebox
from pyecharts.charts import Pie,Page,Grid
from pyecharts.components import Table


from pyecharts import options as opts
from pyecharts.options.global_options import AxisOpts


client = MongoClient('mongodb://localhost:27017/')
db = client['project'] 
#first analysis
def run_query():
     
   
    pipeline = [
        {
            "$match": {
                "description": {"$regex": "Python|SQL", "$options": "i"},
                "formatted_experience_level": {"$ne": None}
            }
        },
        {
            "$lookup": {
                "from": "companies",
                "localField": "company_id",
                "foreignField": "company_id",
                "as": "company_info"
            }
        },
        {"$unwind": "$company_info"},
        {
            "$match": {
                "company_info.country": "US"
            }
        },
        {
            "$lookup": {
                "from": "salaries",
                "localField": "job_id",
                "foreignField": "job_id",
                "as": "salary_info"
            }
        },
        {"$unwind": "$salary_info"},
        {
            "$group": {
                "_id": {
                    "state": "$company_info.state",
                    "experienceLevel": "$formatted_experience_level"
                },
                "averageMedSalary": {"$avg": "$salary_info.med_salary"}
            }
        },
        {
            "$group": {
                "_id": "$_id.state",
                "experienceLevels": {
                    "$push": {
                        "experienceLevel": "$_id.experienceLevel",
                        "averageMedSalary": {"$round": ["$averageMedSalary", 2]}
                    }
                }
            }
        }
    ]

    try:
        results = db.job_postintgs.aggregate(pipeline)
        display_results(results)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# first analyis print format
def display_results(results):
   
    text_area.delete('1.0', tk.END) 

    state_experience_data = []
    headers = ["State", "Experience Level", "Avg Med Salary ($)"]


    for result in results:
        state = result['_id']
        for exp_level in result['experienceLevels']:
            exp = exp_level['experienceLevel']
            avg_salary = exp_level['averageMedSalary']
            state_experience_data.append([state, exp, avg_salary])

    # Create and save the table chart
    title = "Average Median Salary by State and Experience Level"
    subtitle = "Changes in salary offers by experience_level for jobs at each State in US that require Python and SQL skills"
    table_chart = create_table_chart(title, subtitle, headers, state_experience_data)
    page = Page(layout=Page.SimplePageLayout)
    page.add(table_chart)
    page.render("salary_table_chart.html")

    # Display the pie chart link in the text_area
    openAverageSalaryHtml()

def create_table_chart(title, subheading, headers, data):
    table = Table()
    table.add(headers, data)
    table.set_global_opts(
        title_opts=opts.ComponentTitleOpts(title=title, subtitle=subheading),
    )
    return table
#second analysis
def run_query2():
   
    pipeline2 = [
        { "$lookup": {
            "from": "companies",
            "localField": "company_id",
            "foreignField": "company_id",
            "as": "company_info"
        }},
        { "$unwind": "$company_info" },
        { "$match": {
            "company_info.country": "US",
            "company_info.description": { "$regex": "software|engineer|hardware", "$options": "i" }
        }},
        { "$addFields": {
            "hourOfDay": { "$hour": { "$toDate": "$original_listed_time" } },
            "totalApplies": { "$ifNull": ["$applies", 0] },
            "totalViews": { "$ifNull": ["$views", 0] }
        }},
        { "$group": {
            "_id": {
                "applicationType": "$application_type",
                "hourOfDay": "$hourOfDay"
            },
            "totalApplies": { "$sum": "$totalApplies" },
            "totalViews": { "$sum": "$totalViews" }
        }},
        { "$sort": { "_id.hourOfDay": 1, "_id.applicationType": 1 }}
    ]

    try:
        results = db.job_postintgs.aggregate(pipeline2)
        display_results2(results)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def create_table_chart1(title, subtitle, app_types, hours_of_day, total_applies, total_views):
    data = list(zip(app_types, hours_of_day, total_applies, total_views))
    table = (
        Table()
        .add(["Application Type", "Hour of Day", "Total Applies", "Total Views"], data)
        .set_global_opts(
            title_opts=opts.ComponentTitleOpts(title=title, subtitle=subtitle),
        )
    )
    return table

def display_results2(results):
    text_area.delete('1.0', tk.END)

    header = f"{'Application Type':<20} {'HourOfDay':<20} {'Total Applies':<20} {'Total Views':<20}\n"

    app_types, hours_of_day, total_applies, total_views = [], [], [], []

    for result in results:
        app_type = result['_id']['applicationType']
        hour_of_day = result['_id']['hourOfDay']
        total_applies_value = result['totalApplies']
        total_views_value = result['totalViews']

        app_types.append(app_type)
        hours_of_day.append(hour_of_day)
        total_applies.append(total_applies_value)
        total_views.append(total_views_value)

    subtitle = "Changes in applies and views by application type throughout the hour for U.S. companies related to software, engineering, and hardware."
    table_chart  = create_table_chart1("Total Applies and Views by  Hour", subtitle, app_types, hours_of_day, total_applies, total_views)

    page = Page(layout=Page.SimplePageLayout)
    page.add(table_chart)
    page.render("applies_view_chart.html")

    # Display the chart link in the text_area
    openResultChartHtml()

def run_query3():

    pipeline = [
        {
            "$lookup": {
                "from": "companies_industries",
                "localField": "company_id",
                "foreignField": "company_id",
                "as": "industry_info",
            },
        },
        {
            "$lookup": {
                "from": "job_skills",
                "localField": "job_id",
                "foreignField": "job_id",
                "as": "job_info",
            },
        },
        {
            "$lookup": {
                "from": "companies",
                "localField": "company_id",
                "foreignField": "company_id",
                "as": "company_info",
            },
        },
        {
            "$unwind": "$company_info",
        },
        {
            "$unwind": "$job_info",
        },
        {
            "$unwind": "$industry_info",
        },
        {
            "$match": {
                "industry_info.industries": {
                    "$ne": "",
                },
                "closed_time": {
                    "$ne": "",
                },
                "job_info.skill_abr": {
                    "$in": ["IT", "ENG"],
                },
                "company_info.state": {
                    "$in": ["CA", "NY", "TX", "MA"],
                },
            },
        },
        {
            "$addFields": {
                "closed": {
                    "$toLong": "$closed_time",
                },
            },
        },
        {
            "$group": {
                "_id": {
                    "company_id": "$company_id",
                    "industry": "$industry_info.industry",
                    "skill": "$job_info.skill_abr",
                    "sponsored": "$sponsored",
                    "closed": "$closed",
                },
                "jobIDs": {
                    "$addToSet": "$job_id",
                },
            },
        },
        {
            "$project": {
                "_id": 0,
                "company_id": "$_id.company_id",
                "industry": "$_id.industry",
                "skill": "$_id.skill",
                "sponsored": "$_id.sponsored",
                "closed": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {
                            "$toDate": "$_id.closed",
                        },
                    },
                },
                "jobIDs": 1,
            },
        },
        {
            "$sort": {
                "state": 1,
            },
        },
    ]
  
    try:
        results = db.job_postintgs.aggregate(pipeline)
      
        display_result3(results)
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_query4():
        pipeline1 = [
        {
            "$lookup": {
                "from": "companies_industries",
                "localField": "company_id",
                "foreignField": "company_id",
                "as": "industries_info",
            },
        },
        {
            "$unwind": {
                "path": "$industries_info",
            },
        },
        {
            "$match": {
                "industries_info.industry": {"$ne": ""},
                "formatted_work_type": {"$ne": ""},
                "formatted_experience_level": {"$ne": ""},
                "remote_allowed": {"$ne": ""},
                "closed_time": {"$ne": ""},
            },
        },
        {
            "$group": {
                "_id": {
                    "industry": "$industries_info.industry",
                    "formatted_work_type": "$formatted_work_type",
                    "formatted_experience_level": "$formatted_experience_level",
                    "remote_allowed": "$remote_allowed",
                    "closed": "$closed_time",
                    "jobIds": "$job_id",
                },
                "companyIds": {
                    "$addToSet": "$company_id",
                },
            },
        },
        {
            "$project": {
                "_id": 0,
                "industry": "$_id.industry",
                "worktype": "$_id.formatted_work_type",
                "experiencelevel": "$_id.formatted_experience_level",
                "remoteallowed": "$_id.remote_allowed",
                "jobIds": "$_id.jobIds",
                "closed": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {
                            "$toDate": "$_id.closed",
                        },
                    },
                },
            },
        },
        {
            "$sort": {
                "worktype": 1,
                "experiencelevel": 1,
            },
        },
    ]
    
        try:
            resultB = db.job_postintgs.aggregate(pipeline1)
            display_result4(resultB)
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
def display_result3(results):

    industry_total = {}
    industry_sponsored = {}
     
    results = list(results)
    for result in results:
        try:
          industry = result["industry"]
          sponsored = result["sponsored"]
        except KeyError:
          continue  
        # 统计每个行业的总数
        industry_total[industry] = industry_total.get(industry, 0) + 1
        
        if isinstance(sponsored,int) and sponsored == 1:
            industry_sponsored[industry] = industry_sponsored.get(industry, 0) + 1  


    sponsored_percentage = {
        industry: (industry_sponsored.get(industry, 0) / industry_total.get(industry, 0)) * 100
        if industry_total.get(industry, 0) > 0
        else 0
        for industry in industry_total.keys()
    }
    
    total_sponsored = sum(industry_sponsored.values())
    total_industries = sum(industry_total.values())
    total_percentage = total_sponsored / total_industries if total_industries > 0 else 0

    
    pie_chart1 = createPieChart("Proportion of sponsorship by industry",list(sponsored_percentage.items()))
    pie_chart2 = createPieChart("Proportion of sponsorship across all industries", [("1", total_percentage * 100), ("0", 100 - total_percentage * 100)])

    
    page = Page(layout=Page.SimplePageLayout)
    page.add(pie_chart1, pie_chart2)
    page.render("industry_pie_chart.html")
    openEchartHtml()

def display_result4(results):
    industry_data = {}
    for result in results:
       industry  = result.get("industry")
       worktype = result.get("worktype")
       remoteallowed = result.get("remoteallowed")
       
       if(industry,worktype) not in industry_data:
         industry_data[(industry,worktype)] = 0
         
       if remoteallowed == 1.0:
         industry_data[(industry,worktype)] +=1 
    for (industry,worktype), count in industry_data.items():
         print(f"Industry: {industry}, Work Type: {worktype}, Remote Allowed Count: {count}")
    data = [(f"{industry} - {worktype}", count) for (industry, worktype), count in industry_data.items()]  

    pie = Pie()
    pie.add(
        "",
        data,
        radius=["40%","75%"],
        label_opts=opts.LabelOpts(
                position="outside",
                formatter="{b}\n{c}",  # 将行业和工作类型显示在扇形图的下方
                font_size=10,
                font_style="italic",
               
            ),
        itemstyle_opts=opts.ItemStyleOpts(border_radius=15, border_width=2, border_color="white"), 
    ).set_global_opts(title_opts=opts.TitleOpts(title="")
                      ,legend_opts=opts.LegendOpts(is_show=False))  

    grid = (
        Grid()
        .add(pie, grid_opts=opts.GridOpts(pos_bottom="60%"))
        
    )

    grid.render("pie_chart.html")
    openQ2BEchartHtml()

def openAverageSalaryHtml():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    echart_html_path = os.path.join(script_dir, "salary_table_chart.html")
    webbrowser.open("file://" + echart_html_path, new=2)

def openResultChartHtml():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    echart_html_path = os.path.join(script_dir, "applies_views_chart.html")
    webbrowser.open("file://" + echart_html_path, new=2)

def openEchartHtml():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建 HTML 文件的路径
    echart_html_path = os.path.join(script_dir, "industry_pie_chart.html")
    
    webbrowser.open("file://" + echart_html_path, new=2)

def openQ2BEchartHtml():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建 HTML 文件的路径
    echart_html_path = os.path.join(script_dir, "pie_chart.html")
    
    webbrowser.open("file://" + echart_html_path, new=2)
#help to create PieChart 
def createPieChart(title,data):
    pie = Pie()
    pie.add(
       series_name=title,
            data_pair=data,
            radius="55%",
            center=["50%", "60%"],
            itemstyle_opts=opts.ItemStyleOpts(), 
    ).set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="left"),
        tooltip_opts=opts.TooltipOpts(formatter="{a} <br/>{b} : {c}%"),
    )
    return pie



root = tk.Tk()
root.title("MongoDB Query GUI")

#Changes in salary offers by experience_level for jobs at each State in US that require Python and SQL skills
run_button = tk.Button(root, text="Changes in salary offers", command=run_query)
run_button.pack()

#Changes in applies and views by application type throughout the day in August for the U.S companies related to 'software', 'engineer', and 'hardware'
button2 = tk.Button(root, text="Changes in applies and views", command=run_query2)
button2.pack()

button3 = tk.Button(root, text="Proportion of sponsorship by industry", command=run_query3)
button3.pack()

button4 = tk.Button(root,text="Proprotion of allowing remote in all indutries",command=run_query4)
button4.pack()
text_area = tk.Text(root, height=50, width=100)
text_area.pack()

root.mainloop()
