# Project Structure

## Directory Organization

```
├── src/                        # Main application code
│   ├── app.py                  # Entry point and backend initialization
│   ├── data_manager.py         # Abstract base class and LocalJSONBackend
│   ├── google_sheets_backend.py # Google Sheets implementation
│   ├── models.py               # Dataclass definitions
│   └── tabs/                   # UI modules (one per feature)
│       ├── dashboard.py
│       ├── expenses.py
│       ├── milk_sales.py
│       ├── cows.py
│       └── reports.py
├── local_data/                 # JSON storage for local mode
├── tests/                      # Unit tests
└── .kiro/steering/             # AI assistant guidance
```

## Code Organization Patterns

### Data Layer
- **Abstract Interface**: All data operations go through `DataManager` ABC
- **Backend Implementations**: Concrete classes implement the interface
- **Model Classes**: Dataclasses in `models.py` define data structures
- **ID Management**: Auto-generated UUIDs for all entities

### UI Layer
- **Tab Modules**: Each feature has its own module in `src/tabs/`
- **Render Functions**: Each tab module exports a `render(dm: DataManager)` function
- **Session State**: Backend instance stored in `st.session_state.data_manager`

### File Naming Conventions
- **Snake Case**: All Python files use snake_case
- **Descriptive Names**: File names clearly indicate their purpose
- **Test Prefix**: Test files prefixed with `test_`

## Import Patterns

### Path Management
```python
# Standard pattern for imports from src/
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
```

### Module Imports
- Import from `src.` prefix when running from root
- Use relative imports within the same package
- Import specific classes/functions, not entire modules

## Data Flow
1. **UI Layer** → calls methods on DataManager interface
2. **DataManager** → routes to appropriate backend implementation
3. **Backend** → handles persistence (JSON files or Google Sheets)
4. **Models** → provide type safety and structure