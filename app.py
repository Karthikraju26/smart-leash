from flask import Flask, render_template, request, jsonify
from datetime import datetime
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)

data_store = []

DOG_INFO = {
    "name": "JADAL",
    "id": "D001",
    "breed": "GERMAN SHEPHERD",
    "baseline_temp": 38.5,
    "baseline_bark": 5,
    "baseline_rest": 40
}

@app.route("/")
def dashboard():

    if not data_store:
        demo_data = {
            "temperature": 39.2,
            "bark_frequency": 12,
            "restlessness": 65,
            "risk_level": "MEDIUM",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data_store.append(demo_data)

    latest = data_store[-1]

    times = [d["timestamp"] for d in data_store]
    rest = [d["restlessness"] for d in data_store]
    amplitudes = [d.get("bark_amplitude", 0) for d in data_store]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=times,
        y=rest,
        mode='lines+markers',
        name='Restlessness',
        line=dict(color='cyan', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=[DOG_INFO["baseline_rest"]] * len(times),
        mode='lines',
        name='Baseline',
        line=dict(color='rgb(176,157,11)', dash='dash')
    ))

    fig.update_layout(
        title="Restlessness Trend",
        height=450,
        plot_bgcolor="rgb(91,55,55)",
        paper_bgcolor="rgb(57,26,26)",
        font=dict(color="white")
    )

    graph_html = pio.to_html(fig, full_html=False)

    bark_fig = go.Figure()

    bark_fig.add_trace(go.Scatter(
    x=times,
    y=amplitudes,
    mode='lines+markers',
    name='Bark Amplitude',
    line=dict(color='orange')
    ))

    bark_fig.update_layout(
    title="Bark Activity",
    height=350,
    plot_bgcolor="rgb(91,55,55)",
    paper_bgcolor="rgb(57,26,26)",
    font=dict(color="white")
)

    bark_graph_html = pio.to_html(bark_fig, full_html=False)

    risk_map = {"SAFE": 10, "MEDIUM": 50, "HIGH": 90}
    risk_value = risk_map.get(latest["risk_level"], 10)

    gauge = go.Figure(go.Indicator(
        mode="gauge",
        value=risk_value,
        gauge={
            "axis": {"range": [0, 100], "visible": False},
            "bar": {"color": "white"},
            "steps": [
                {"range": [0, 33], "color": "green"},
                {"range": [33, 66], "color": "yellow"},
                {"range": [66, 100], "color": "red"}
            ]
        }
    ))

    gauge.update_layout(
        height=300,
        paper_bgcolor="rgb(57,26,26)",
        font=dict(color="white")
    )

    gauge_html = pio.to_html(gauge, full_html=False)

    return render_template(
    "dashboard.html",
    dog=DOG_INFO,
    latest=latest,
    graph=graph_html,
    bark_graph=bark_graph_html,
    gauge=gauge_html
    )


@app.route("/receive", methods=["POST"])
def receive_data():

    incoming = request.json

    print("\n====================")
    print(incoming)
    print("====================")

    incoming["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_store.append(incoming)

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(debug=True)