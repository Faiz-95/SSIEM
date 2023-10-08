from flask import Flask, jsonify, render_template, url_for, redirect, flash, session
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from elasticsearch import Elasticsearch
from flask_login import LoginManager, UserMixin, login_required


import plotly.io as pio

from visualisations.agent_info_table import create_agent_info_table
from visualisations.alert_severity_pie_chart import create_alert_severity_pie_chart
from visualisations.alerts_per_agent_area_chart import create_alerts_per_agent_area_chart
from visualisations.distribution_alert_severity_line_graph import create_distribution_alert_severity_line_graph
from visualisations.event_logs_table import create_event_logs_table
from visualisations.mitre_attacks_donut_chart import create_top_mitre_attacks_donut_chart
from visualisations.top_events_donut_chart import create_top_events_donut_chart
from visualisations.auth_failures_histogram import create_auth_failures_histogram
from visualisations.total_agent_alerts_bar_graph import create_total_agent_alerts_bar_graph
from data.login_data import authenticate_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKey'
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem session
app.config['SESSION_PERMANENT'] = False
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

es = Elasticsearch(['elasticsearch:9200'], # ES Connection To elastic DB
                   use_ssl=True,    
                   verify_certs=False,
                   scheme="https", 
                   http_auth=('admin', 'admin'))

pio.renderers.default = 'browser'  # set the default renderer to browser


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = StringField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

#Home page
@app.route('/home') 
def home():
    return render_template('home.html')

@app.route("/addUser")
def addUser():
    return render_template("addUser.html")


#Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate_user(es, username, password):
            session['username'] = username
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/test_es')
def test_es_connection():
    try:
        res = es.info()
        return jsonify(res)
    except Exception as e:
        return str(e)


#Account management page
@app.route('/management') 
def management():
    return render_template('management.html')


@app.route('/dashboard')
def dashboard():
    agent_info_table = create_agent_info_table(es)

    alert_severity_pie_chart = create_alert_severity_pie_chart(es)
    top_events_donut_chart = create_top_events_donut_chart(es)
    mitre_attacks_donut_chart = create_top_mitre_attacks_donut_chart(es)

    distribution_alert_severity_line_graph = create_distribution_alert_severity_line_graph(es)
    auth_failures_histogram = create_auth_failures_histogram(es)
    total_agent_alerts_bar_graph = create_total_agent_alerts_bar_graph(es)

    alerts_per_agent_area_chart = create_alerts_per_agent_area_chart(es) 

    event_logs_table = create_event_logs_table(es)
    
    
    return render_template('dashboard.html',
                           agent_info_table = agent_info_table,
                           
                           alert_severity_pie_chart = alert_severity_pie_chart,
                           top_events_donut_chart = top_events_donut_chart,
                           mitre_attacks_donut_chart = mitre_attacks_donut_chart,

                           distribution_alert_severity_line_graph = distribution_alert_severity_line_graph, 
                           auth_failures_histogram = auth_failures_histogram,
                           total_agent_alerts_bar_graph = total_agent_alerts_bar_graph,

                           alerts_per_agent_area_chart=alerts_per_agent_area_chart,
                           
                           event_logs_table = event_logs_table
                           )

@app.route('/dashboard_data')
def dashboard_data():
    agent_info_table = create_agent_info_table(es)
  
    alert_severity_pie_chart = create_alert_severity_pie_chart(es)
    top_events_donut_chart = create_top_events_donut_chart(es)
    mitre_attacks_donut_chart = create_top_mitre_attacks_donut_chart(es)

    distribution_alert_severity_line_graph = create_distribution_alert_severity_line_graph(es)
    auth_failures_histogram = create_auth_failures_histogram(es)
    total_agent_alerts_bar_graph = create_total_agent_alerts_bar_graph(es)

    alerts_per_agent_area_chart = create_alerts_per_agent_area_chart(es) 

    event_logs_table = create_event_logs_table(es)
    
    return jsonify(
        agent_info_table=agent_info_table,

        alert_severity_pie_chart=alert_severity_pie_chart,
        top_events_donut_chart = top_events_donut_chart,
        mitre_attacks_donut_chart = mitre_attacks_donut_chart,

        distribution_alert_severity_line_graph = distribution_alert_severity_line_graph,
        auth_failures_histogram = auth_failures_histogram,
        total_agent_alerts_bar_graph = total_agent_alerts_bar_graph,

        alerts_per_agent_area_chart = alerts_per_agent_area_chart,

        event_logs_table=event_logs_table
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(5000), debug=True)