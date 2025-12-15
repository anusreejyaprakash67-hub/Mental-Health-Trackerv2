from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_random_key"

# --- Questions (21) ---
questions = [
    "I found it hard to wind down.",
    "I was aware of dryness of my mouth.",
    "I couldn’t seem to experience any positive feeling at all.",
    "I experienced breathing difficulty.",
    "I found it difficult to work up the initiative to do things.",
    "I tended to over-react to situations.",
    "I experienced trembling.",
    "I felt that I was using a lot of nervous energy.",
    "I was worried about situations in which I might panic.",
    "I felt down-hearted and blue.",
    "I found myself getting agitated.",
    "I found it difficult to relax.",
    "I felt that I was close to panic.",
    "I felt I wasn’t worth much as a person.",
    "I felt that I was rather touchy.",
    "I felt scared without any good reason.",
    "I felt that life was meaningless.",
    "I experienced heart palpitations.",
    "I felt that I had nothing to look forward to.",
    "I felt restless and fidgety.",
    "I felt that I was intolerant of anything."
]

# --- Index groups (0-based indices into `questions`) ---
depression_idx = [2, 4, 9, 13, 16, 18]               # 6 items
anxiety_idx    = [1, 3, 6, 8, 11, 14, 17]            # 7 items
stress_idx     = [0, 5, 7, 10, 12, 15, 19, 20]       # 8 items

# --- Severity classification functions ---
def classify_depression(score):
    # DASS-21 scaled by 2 usual thresholds
    if score <= 9: return "Normal"
    if 10 <= score <= 13: return "Mild"
    if 14 <= score <= 20: return "Moderate"
    if 21 <= score <= 27: return "Severe"
    return "Extremely Severe"

def classify_anxiety(score):
    if score <= 7: return "Normal"
    if 8 <= score <= 9: return "Mild"
    if 10 <= score <= 14: return "Moderate"
    if 15 <= score <= 19: return "Severe"
    return "Extremely Severe"

def classify_stress(score):
    if score <= 14: return "Normal"
    if 15 <= score <= 18: return "Mild"
    if 19 <= score <= 25: return "Moderate"
    if 26 <= score <= 33: return "Severe"
    return "Extremely Severe"

# --- Advice mapping: only the single advice for the computed severity will be shown ---
ADVICE = {
    "Depression": {
        "Normal": "No clinical sign of depression. Keep maintaining healthy routines: regular sleep, exercise, and social connection.",
        "Mild": "Mild depressive symptoms—try journaling, light exercise, structured routine, and talking with someone you trust.",
        "Moderate": "Moderate depression—consider starting brief therapy or counseling and using structured behavioral activation techniques.",
        "Severe": "Severe symptoms—please seek professional mental health support (therapist/psychiatrist) soon.",
        "Extremely Severe": "Extremely severe symptoms—contact a mental health professional immediately; if at risk, seek urgent care."
    },
    "Anxiety": {
        "Normal": "No current clinical anxiety. Continue relaxation habits and stress management.",
        "Mild": "Mild anxiety—practice daily breathing exercises, short mindfulness sessions, and reduce stimulants.",
        "Moderate": "Moderate anxiety—try guided CBT techniques, regular exercise, and consider talking to a counselor.",
        "Severe": "Severe anxiety—consult a mental health professional; consider structured therapy and medical advice if needed.",
        "Extremely Severe": "Extremely severe anxiety—seek urgent professional help; if incapacitated, contact emergency services."
    },
    "Stress": {
        "Normal": "Stress levels are within normal limits. Keep balanced work-rest cycles and self-care.",
        "Mild": "Mild stress—use time management, short relaxation breaks, and hobbies to unwind.",
        "Moderate": "Moderate stress—prioritise tasks, set boundaries, and consider short-term counseling if helpful.",
        "Severe": "Severe stress—speak to a professional or counsellor; consider stress-management programs.",
        "Extremely Severe": "Extremely severe stress—seek urgent support from a mental health professional."
    }
}

# --- helper to compute scores ---
def compute_scores(answers):
    # answers: list of 21 ints (0-3)
    dep = sum(answers[i] for i in depression_idx) * 2
    anx = sum(answers[i] for i in anxiety_idx) * 2
    strt = sum(answers[i] for i in stress_idx) * 2
    return dep, anx, strt

@app.route('/')
def home():
    # reset answers
    session['answers'] = []
    return render_template('index.html')

@app.route('/question/<int:q_no>', methods=['GET', 'POST'])
def question(q_no):
    # q_no is 1-based (1..21)
    if 'answers' not in session:
        session['answers'] = []
    answers = session.get('answers', [])

    # handle POST
    if request.method == 'POST':
        try:
            ans = int(request.form['answer'])
        except:
            ans = 0
        answers.append(ans)
        session['answers'] = answers

        # if last question -> show result
        if q_no >= len(questions):
            return redirect(url_for('result'))
        return redirect(url_for('question', q_no=q_no + 1))

    # guard: if someone navigates beyond last question
    if q_no < 1:
        return redirect(url_for('question', q_no=1))
    if q_no > len(questions):
        return redirect(url_for('result'))

    return render_template('question.html', question=questions[q_no - 1], q_no=q_no, total=len(questions))

@app.route('/result')
def result():
    answers = session.get('answers', [])
    # if incomplete, fill with zeros to avoid crash (best-effort)
    if len(answers) < len(questions):
        answers = answers + [0] * (len(questions) - len(answers))

    dep_score, anx_score, str_score = compute_scores(answers)

    dep_sev = classify_depression(dep_score)
    anx_sev = classify_anxiety(anx_score)
    str_sev = classify_stress(str_score)

    # Only give the single advice matching their current severity for each category
    dep_advice = ADVICE["Depression"][dep_sev]
    anx_advice = ADVICE["Anxiety"][anx_sev]
    str_advice = ADVICE["Stress"][str_sev]

    # Pass numeric values and labels for the animated chart (Chart.js)
    chart_data = {
        "labels": ["Depression", "Anxiety", "Stress"],
        "values": [dep_score, anx_score, str_score]
    }

    return render_template(
        'result.html',
        dep_score=dep_score, anx_score=anx_score, str_score=str_score,
        dep_sev=dep_sev, anx_sev=anx_sev, str_sev=str_sev,
        dep_advice=dep_advice, anx_advice=anx_advice, str_advice=str_advice,
        chart_data=chart_data
    )

if __name__ == "__main__":
    # set debug=False in production
    app.run(debug=True)
