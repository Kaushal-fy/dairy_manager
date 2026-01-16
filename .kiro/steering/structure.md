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
- **Mobile-Responsive Design**: Card-based layouts for data tables instead of column grids
- **Action Buttons**: Edit (✏️) and Delete (🗑️) buttons in consistent positions

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


## UI Design Patterns

### Mobile-Responsive Tables
All data tables use a card-based layout for mobile compatibility:
- **Container Pattern**: Each record wrapped in `st.container()`
- **Two-Column Layout**: Main content (4 parts) + Actions (1 part)
- **Visual Hierarchy**: Bold headers, caption details, dividers between records
- **Action Buttons**: Vertically stacked edit/delete buttons in right column

### Example Pattern:
```python
for item in items:
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item.primary_field}** | {item.secondary}")
            st.caption(f"Details: {item.details}")
        with col2:
            if st.button("✏️", key=f"edit_{item.id}"):
                # Edit logic
            if st.button("🗑️", key=f"del_{item.id}"):
                # Delete logic
        st.divider()
```