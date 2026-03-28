from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/students")
def students():
    data = [
        {
            "name": "Sabine Klein",
            "score": 23,
            "status": "At Risk",
            "work_done": 8,
            "work_total": 36,
            "seeking_attention": "High",
            "working_towards": "Basic Literacy",
            "handover": "Urgent"
        },
        {
            "name": "Dania Federizana",
            "score": 53,
            "status": "Average",
            "work_done": 20,
            "work_total": 36,
            "seeking_attention": "Medium",
            "working_towards": "Grade Level",
            "handover": "Monitor"
        },
        {
            "name": "Susan Chan",
            "score": 82,
            "status": "On Track",
            "work_done": 33,
            "work_total": 36,
            "seeking_attention": "Low",
            "working_towards": "Advanced",
            "handover": "None"
        },
        {
            "name": "Marcus Kim",
            "score": 41,
            "status": "Struggling",
            "work_done": 14,
            "work_total": 36,
            "seeking_attention": "High",
            "working_towards": "Grade Level",
            "handover": "Review"
        },
        {
            "name": "Aisha Patel",
            "score": 76,
            "status": "On Track",
            "work_done": 30,
            "work_total": 36,
            "seeking_attention": "Low",
            "working_towards": "Advanced",
            "handover": "None"
        },
        {
            "name": "Leo Brennan",
            "score": 61,
            "status": "Average",
            "work_done": 24,
            "work_total": 36,
            "seeking_attention": "Medium",
            "working_towards": "Grade Level",
            "handover": "Monitor"
        },
    ]
    return jsonify(data)

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)