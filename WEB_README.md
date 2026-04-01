# Web UI & API Directory

## Contents
- `app.py` - Streamlit web interface
- `requirements-ui.txt` - UI dependencies
- `WEB_UI_GUIDE.md` - UI documentation

## Future Structure
```
web/
├── streamlit/           # Streamlit UI
│   ├── app.py          # Main app
│   ├── pages/          # Multi-page support
│   └── components/     # Reusable components
├── api/                # FastAPI endpoints
│   ├── main.py
│   └── routes/
└── frontend/           # React/Vue UI (future)
    └── src/
```

## Development Notes
- Currently using Streamlit for rapid UI development
- Can be extended with FastAPI for REST API
- Can add React/Vue for advanced frontend

See [WEB_UI_GUIDE.md](./WEB_UI_GUIDE.md) for setup instructions.
