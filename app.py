from flask import Flask, render_template,request ,redirect,url_for,session
from database import init_db,get_db_connection
import joblib

app = Flask(__name__)
app.secret_key = "studybuddy_secrect_key"
model = joblib.load("performance_model.pkl")

# Initialize database
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("dashboard"))

        else:
            return "Invalid email or password!"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()

        except Exception as e:
            conn.close()
            return f"Registration failed: {e}"

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    performances = conn.execute("""
        SELECT *
        FROM performance
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        performances=performances
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/performance", methods=["GET", "POST"])
def performance():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        subject = request.form["subject"]
        marks = float(request.form["marks"])
        attendance = float(request.form["attendance"])
        study_hours = float(request.form["study_hours"])

        # ML Prediction
        prediction = model.predict([
            [marks, attendance, study_hours]
        ])[0]

        prediction = round(prediction, 2)

        # Performance Level
        if prediction >= 80:
            level = "Excellent"
            recommendation = "Keep up the good work! Revise regularly and practice advanced questions."
            study_plan = "2 hours/day"

        elif prediction >= 60:
            level = "Good"
            recommendation = "Your performance is good. Focus on revision and regular practice."
            study_plan = "3 hours/day"

        else:
            level = "Needs Improvement"
            recommendation = "Focus on your weak subjects and increase your daily study time."
            study_plan = "4 hours/day"

        # Save performance in database
        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO performance
                (user_id, subject, marks, attendance, study_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                subject,
                marks,
                attendance,
                study_hours
            ))

            conn.commit()

        except Exception as e:
            conn.close()
            return f"Performance save failed: {e}"

        conn.close()

        return render_template(
            "prediction.html",
            subject=subject,
            prediction=prediction,
            level=level,
            recommendation=recommendation,
            study_plan=study_plan
        )

    return render_template("performance.html")
@app.route("/delete_performance/<int:performance_id>", methods=["POST"])
def delete_performance(performance_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM performance
        WHERE id = ? AND user_id = ?
    """, (
        performance_id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)