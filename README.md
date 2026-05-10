# monmacro

Mongolian macroeconomic indicators, reports, and dashboard.

## Streamlit dashboard

Install the dashboard dependencies:

```powershell
pip install -r requirements.txt
```

Create an allowed-user secrets file:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
python tools\create_password_hash.py
```

Paste the generated hash into `.streamlit/secrets.toml` for each allowed user.

Run the dashboard:

```powershell
streamlit run app.py
```
