# LeagueOfSheetsStats

---

# 🛡️ LeagueOfSheetsStats

A simple script to fetch and analyze recent **ranked League of Legends match stats** using the Riot Games API. Outputs match summaries in a tab-separated format ready for Excel and automatically copies it to your clipboard.

## 📦 Features

- Fetches recent ranked match data using your Riot ID
- Extracts key stats: KDA, CS/min, vision score, gold/min, and more
- Formats data for Excel with calculated columns
- Copies results to clipboard for quick pasting
- Uses [Rich](https://github.com/Textualize/rich) for styled terminal output

## ⚙️ Requirements

- Python 3.?
- Riot Games API Key ([Get one here](https://developer.riotgames.com/))

## 📥 Installation & Run (Windows)

```bash
pip install -r requirements.txt && python main.py
```

Just paste it into Google Sheets or Excel — calculated fields are ready!
