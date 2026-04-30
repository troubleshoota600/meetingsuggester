from flask import Flask, render_template, request
from datetime import datetime
from dateutil import tz

app = Flask(__name__)

def parse_time(t_str):
    return datetime.strptime(t_str, "%H:%M").time()

def get_timezone(tz_name):
    return tz.gettz(tz_name)

def find_overlap(intervals):
    latest_start = max(start for start, end in intervals)
    earliest_end = min(end for start, end in intervals)
    return (latest_start, earliest_end) if latest_start < earliest_end else None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    meeting_utc = None

    if request.method == "POST":
        names = request.form.getlist("name")
        tzs = request.form.getlist("timezone")
        starts = request.form.getlist("start")
        ends = request.form.getlist("end")

        intervals = []
        participants = []

        for i in range(len(names)):
            timezone = get_timezone(tzs[i])
            today = datetime.now(timezone).date()

            start_dt = datetime.combine(today, parse_time(starts[i])).replace(tzinfo=timezone)
            end_dt = datetime.combine(today, parse_time(ends[i])).replace(tzinfo=timezone)

            intervals.append((start_dt.astimezone(tz.UTC), end_dt.astimezone(tz.UTC)))
            participants.append((names[i], timezone))

        overlap = find_overlap(intervals)

        if overlap:
            start, end = overlap
            meeting_time = start + (end - start) / 2

            meeting_utc = meeting_time.astimezone(tz.UTC).strftime('%Y-%m-%d %H:%M UTC')

            result = []
            for name, timezone in participants:
                local_time = meeting_time.astimezone(timezone)
                result.append(f"{name}: {local_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            result = ["No common time found"]

    return render_template("index.html", result=result, meeting_utc=meeting_utc)

if __name__ == "__main__":
    app.run(debug=True)