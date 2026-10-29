# NL → CLI (Prompt Engineering)

Agent שממיר הוראה בשפה טבעית (עברית/אנגלית) לפקודת CLI אחת, עם שכבת בטיחות.

## התקנה והרצה (uv)
```bash
uv sync
cp .env.example .env        # והכניסי ANTHROPIC_API_KEY
uv run nl2cli-app           # ממשק Gradio
```

## הרצת תרחישי בדיקה לאיטרציה
```bash
uv run nl2cli-eval --iteration 1 --prompt v1
uv run nl2cli-eval --iteration 2 --prompt v2
uv run nl2cli-eval --iteration 3 --prompt v3
uv run nl2cli-eval --iteration 4 --prompt v4
```
כל הרצה יוצרת `results/iteration_N.csv` עם 30 תרחישים (אותם תרחישים בכל איטרציה, כדי שאפשר יהיה להשוות).

## יצירת ה-Google Sheet
1. צרי Sheet חדש. לכל איטרציה: File → Import → Upload → `iteration_N.csv` → "Insert new sheet(s)".
2. עמודות אוטומטיות: `format_ok`, `syntax_ok`, `safety_status`, `safety_match`.
3. עמודות ידניות: `correct` (תקין / שגוי) ו-`notes` - תמלאי לפי שיקול דעתך.
4. מומלץ להוסיף גיליון סיכום עם `=SUM()` לכל מדד בכל איטרציה.

## מבנה
- `prompts/` - גרסאות הפרומפט (v1→v4), כל גרסה משפרת בעיה אחת.
- `scenarios/scenarios.csv` - 30 תרחישים: בסיסיים, מסוכנים, דו-משמעיים, רב-שלביים, prompt injection.
- `src/nl2cli/safety.py` - סיווג פלט (SAFE/RISKY/BLOCKED) בקוד, בנפרד מהפרומפט.
- `docs/experiment_log.md` - יומן ניסויים למילוי.

## הערות
- ברירת מחדל: Windows (cmd). אפשר לשנות ב-`.env` עם `TARGET_OS`.
- בדיקת התחביר היא היוריסטיקה (פקודה מוכרת + מרכאות מאוזנות), לא parser אמיתי.
- התוצאות לא מולאו מראש - הן תלויות בהרצה שלך מול המודל.
