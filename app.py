import os
import pickle
import numpy as np
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Correct model filename matching your uploaded file
MODEL_PATH = "DecisoinTree.pkl"

model = None
if os.path.exists(MODEL_PATH):
  with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# HTML Layout with Dark Theme UI & Modern Styling
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campus Placement Predictor</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #161b26;
            --input-bg: #0d1117;
            --border-color: #212636;
            --accent-color: #6366f1;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --success-color: #10b981;
            --error-color: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 30px 15px;
        }

        .container {
            width: 100%;
            max-width: 850px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 35px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .header p {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }

        .form-group input, .form-group select {
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 14px;
            color: var(--text-primary);
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .form-group input:focus, .form-group select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
        }

        .submit-btn {
            grid-column: 1 / -1;
            margin-top: 15px;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: #ffffff;
            border: none;
            padding: 14px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }

        .result-card {
            margin-top: 30px;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 1.1rem;
        }

        .result-card.placed {
            background-color: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--success-color);
            color: var(--success-color);
        }

        .result-card.not-placed {
            background-color: rgba(239, 68, 68, 0.15);
            border: 1px solid var(--error-color);
            color: var(--error-color);
        }

        .alert-error {
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--error-color);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🎓 Placement Predictor Portal</h1>
        <p>Fill in candidate credentials to evaluate placement status</p>
    </div>

    {% if error_msg %}
    <div class="alert-error">{{ error_msg }}</div>
    {% endif %}

    <form method="POST" action="/predict">
        <div class="form-grid">
            <div class="form-group">
                <label>Gender</label>
                <select name="gender" required>
                    <option value="M" {% if form_data and form_data['gender'] == 'M' %}selected{% endif %}>Male</option>
                    <option value="F" {% if form_data and form_data['gender'] == 'F' %}selected{% endif %}>Female</option>
                </select>
            </div>

            <div class="form-group">
                <label>SSC Percentage (%)</label>
                <input type="number" step="0.01" name="ssc_p" min="0" max="100" value="{{ form_data['ssc_p'] if form_data else '75.0' }}" required>
            </div>

            <div class="form-group">
                <label>SSC Board</label>
                <select name="ssc_b" required>
                    <option value="Central" {% if form_data and form_data['ssc_b'] == 'Central' %}selected{% endif %}>Central</option>
                    <option value="Others" {% if form_data and form_data['ssc_b'] == 'Others' %}selected{% endif %}>Others</option>
                </select>
            </div>

            <div class="form-group">
                <label>HSC Percentage (%)</label>
                <input type="number" step="0.01" name="hsc_p" min="0" max="100" value="{{ form_data['hsc_p'] if form_data else '70.0' }}" required>
            </div>

            <div class="form-group">
                <label>HSC Board</label>
                <select name="hsc_b" required>
                    <option value="Central" {% if form_data and form_data['hsc_b'] == 'Central' %}selected{% endif %}>Central</option>
                    <option value="Others" {% if form_data and form_data['hsc_b'] == 'Others' %}selected{% endif %}>Others</option>
                </select>
            </div>

            <div class="form-group">
                <label>HSC Stream</label>
                <select name="hsc_s" required>
                    <option value="Science" {% if form_data and form_data['hsc_s'] == 'Science' %}selected{% endif %}>Science</option>
                    <option value="Commerce" {% if form_data and form_data['hsc_s'] == 'Commerce' %}selected{% endif %}>Commerce</option>
                    <option value="Arts" {% if form_data and form_data['hsc_s'] == 'Arts' %}selected{% endif %}>Arts</option>
                </select>
            </div>

            <div class="form-group">
                <label>Degree Percentage (%)</label>
                <input type="number" step="0.01" name="degree_p" min="0" max="100" value="{{ form_data['degree_p'] if form_data else '68.0' }}" required>
            </div>

            <div class="form-group">
                <label>Degree Type</label>
                <select name="degree_t" required>
                    <option value="Sci&Tech" {% if form_data and form_data['degree_t'] == 'Sci&Tech' %}selected{% endif %}>Sci & Tech</option>
                    <option value="Comm&Mgmt" {% if form_data and form_data['degree_t'] == 'Comm&Mgmt' %}selected{% endif %}>Comm & Mgmt</option>
                    <option value="Others" {% if form_data and form_data['degree_t'] == 'Others' %}selected{% endif %}>Others</option>
                </select>
            </div>

            <div class="form-group">
                <label>Work Experience</label>
                <select name="workex" required>
                    <option value="No" {% if form_data and form_data['workex'] == 'No' %}selected{% endif %}>No</option>
                    <option value="Yes" {% if form_data and form_data['workex'] == 'Yes' %}selected{% endif %}>Yes</option>
                </select>
            </div>

            <div class="form-group">
                <label>Employability Test (%)</label>
                <input type="number" step="0.01" name="etest_p" min="0" max="100" value="{{ form_data['etest_p'] if form_data else '70.0' }}" required>
            </div>

            <div class="form-group">
                <label>MBA Specialisation</label>
                <select name="specialisation" required>
                    <option value="Mkt&Fin" {% if form_data and form_data['specialisation'] == 'Mkt&Fin' %}selected{% endif %}>Mkt & Fin</option>
                    <option value="Mkt&HR" {% if form_data and form_data['specialisation'] == 'Mkt&HR' %}selected{% endif %}>Mkt & HR</option>
                </select>
            </div>

            <div class="form-group">
                <label>MBA Percentage (%)</label>
                <input type="number" step="0.01" name="mba_p" min="0" max="100" value="{{ form_data['mba_p'] if form_data else '65.0' }}" required>
            </div>

            <button type="submit" class="submit-btn">🚀 Predict Status</button>
        </div>
    </form>

    {% if prediction_text %}
    <div class="result-card {% if is_placed %}placed{% else %}not-placed{% endif %}">
        {{ prediction_text }}
    </div>
    {% endif %}
</div>

</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
  error_msg = None
  if model is None:
    error_msg = f"Model file '{MODEL_PATH}' not found on server. Please ensure it is uploaded."
  return render_template_string(HTML_LAYOUT, error_msg=error_msg)


@app.route("/predict", methods=["POST"])
def predict():
  if model is None:
    return render_template_string(HTML_LAYOUT, error_msg="Model file is missing.")

  try:
    form_data = request.form.to_dict()

    gender = 1 if form_data.get("gender") == "M" else 0
    ssc_p = float(form_data.get("ssc_p", 0.0))
    ssc_b = 1 if form_data.get("ssc_b") == "Central" else 0
    hsc_p = float(form_data.get("hsc_p", 0.0))
    hsc_b = 1 if form_data.get("hsc_b") == "Central" else 0

    hsc_s_map = {"Science": 0, "Commerce": 1, "Arts": 2}
    hsc_s = hsc_s_map.get(form_data.get("hsc_s"), 0)

    degree_p = float(form_data.get("degree_p", 0.0))

    degree_t_map = {"Sci&Tech": 0, "Comm&Mgmt": 1, "Others": 2}
    degree_t = degree_t_map.get(form_data.get("degree_t"), 0)

    workex = 1 if form_data.get("workex") == "Yes" else 0
    etest_p = float(form_data.get("etest_p", 0.0))

    spec_map = {"Mkt&Fin": 0, "Mkt&HR": 1}
    specialisation = spec_map.get(form_data.get("specialisation"), 0)

    mba_p = float(form_data.get("mba_p", 0.0))

    input_features = np.array([[
        gender, ssc_p, ssc_b, hsc_p, hsc_b, hsc_s,
        degree_p, degree_t, workex, etest_p, specialisation, mba_p
    ]])

    prediction = model.predict(input_features)[0]

    is_placed = (
        prediction == 1
        or prediction == "Placed"
        or str(prediction).lower() == "placed"
    )

    if is_placed:
      prediction_text = "🎉 Candidate Status: PLACED — High chance of securing a placement!"
    else:
      prediction_text = "⚠️ Candidate Status: NOT PLACED — Candidate may require performance improvement."

    return render_template_string(
        HTML_LAYOUT,
        prediction_text=prediction_text,
        is_placed=is_placed,
        form_data=form_data,
    )

  except Exception as e:
    return render_template_string(
        HTML_LAYOUT, error_msg=f"Error in processing input: {str(e)}"
    )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=False)