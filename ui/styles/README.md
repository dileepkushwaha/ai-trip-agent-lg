# UI Styles Module

This directory contains centralized styling and theming for the AI Trip Agent UI.

## Files

### `theme.py`
Central theme configuration module that provides:
- Color scheme definitions for light and dark themes
- CSS generation functions for different page types
- Modular styling system

## Usage

### In Your Streamlit App

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from styles.theme import THEMES, get_theme_css

# Get current theme
current_theme = THEMES[st.session_state.theme]

# Apply CSS (choose page type: "main" or "observability")
st.markdown(get_theme_css(current_theme, page_type="main"), unsafe_allow_html=True)
```

## Modifying Themes

### Changing Colors

Edit the `THEMES` dictionary in `theme.py`:

```python
THEMES = {
    "light": {
        "bg_primary": "#ffffff",      # Main background
        "bg_secondary": "#f0f2f6",    # Secondary background
        "bg_sidebar": "#f8f9fa",      # Sidebar background
        "text_primary": "#1f1f1f",    # Primary text
        "text_secondary": "#4a4a4a",  # Secondary text
        "accent": "#1976d2",          # Accent color
        "success": "#2e7d32",         # Success color
        "warning": "#f57c00",         # Warning color
        "danger": "#d32f2f",          # Danger color
        # ... more colors
    },
    "dark": {
        # Same keys with different values
    }
}
```

### Adding New Styles

1. **For all pages**: Edit `get_base_css()` function
2. **For main app only**: Edit `get_main_app_css()` function
3. **For observability only**: Edit `get_observability_css()` function

### Creating a New Page Type

```python
def get_my_page_css(theme: dict) -> str:
    """Generate CSS for my custom page."""
    return f"""
    <style>
        .my-custom-class {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
        }}
    </style>
    """

# Update get_theme_css() to include your page type
def get_theme_css(theme: dict, page_type: str = "main") -> str:
    base = get_base_css(theme)
    
    if page_type == "main":
        return base + get_main_app_css(theme)
    elif page_type == "observability":
        return base + get_observability_css(theme)
    elif page_type == "my_page":
        return base + get_my_page_css(theme)
    else:
        return base
```

## Theme Structure

### Color Keys

| Key | Purpose | Example (Light) | Example (Dark) |
|-----|---------|----------------|----------------|
| `bg_primary` | Main background | `#ffffff` | `#0e1117` |
| `bg_secondary` | Cards, containers | `#f0f2f6` | `#262730` |
| `bg_sidebar` | Sidebar background | `#f8f9fa` | `#1a1d24` |
| `text_primary` | Main text | `#1f1f1f` | `#fafafa` |
| `text_secondary` | Muted text | `#4a4a4a` | `#b0b0b0` |
| `accent` | Highlights, links | `#1976d2` | `#42a5f5` |
| `success` | Success states | `#2e7d32` | `#66bb6a` |
| `warning` | Warning states | `#f57c00` | `#ffa726` |
| `danger` | Error states | `#d32f2f` | `#ef5350` |
| `user_msg` | User message bg | `#e3f2fd` | `#1e3a5f` |
| `assistant_msg` | Assistant msg bg | `#e8f5e9` | `#1a3a1a` |
| `border` | Border color | `#dee2e6` | `#404040` |
| `button_bg` | Button background | `#1976d2` | `#42a5f5` |
| `button_text` | Button text | `#ffffff` | `#ffffff` |

### CSS Modules

#### Base CSS (`get_base_css()`)
Applied to all pages:
- Global app background
- Sidebar styling
- Button styling (CRITICAL for visibility)
- Form controls (select, input, checkbox, etc.)
- Dropdown menus
- Headers

#### Main App CSS (`get_main_app_css()`)
Specific to `streamlit_app.py`:
- Message boxes (user, assistant, agent)
- Info boxes (carbon, itinerary, agent status)
- Option cards
- Custom headers

#### Observability CSS (`get_observability_css()`)
Specific to observability dashboard:
- Metric cards
- Agent cards
- Trace cards
- Status badges

## Troubleshooting

### Buttons Not Visible

If buttons appear with dark text on dark background:

1. Check that `button_bg` and `button_text` are defined in both themes
2. Ensure `!important` is used in button CSS rules
3. Verify the theme is being applied: `st.markdown(get_theme_css(...), unsafe_allow_html=True)`

### Sidebar Text Not Visible

1. Check `bg_sidebar` and `text_primary` contrast
2. Ensure sidebar CSS rules include `!important`
3. Verify all text elements are covered in sidebar CSS

### Theme Not Updating

1. Restart Streamlit app after modifying `theme.py`
2. Clear browser cache
3. Check for CSS syntax errors in browser console

## Best Practices

1. **Always use theme colors**: Never hardcode colors in your Streamlit code
2. **Test both themes**: Verify visibility in both light and dark modes
3. **Use semantic names**: Use `success`, `warning`, `danger` instead of `green`, `orange`, `red`
4. **Maintain consistency**: Keep the same keys in both light and dark themes
5. **Document changes**: Add comments when modifying theme colors

## Examples

### Using Theme Colors in Markdown

```python
st.markdown(f"""
<div style="background-color: {current_theme['bg_secondary']}; 
            color: {current_theme['text_primary']}; 
            padding: 1rem; 
            border-radius: 0.5rem;">
    This text will be visible in both themes!
</div>
""", unsafe_allow_html=True)
```

### Creating Custom Cards

```python
st.markdown(f"""
<div style="background: {current_theme['bg_secondary']};
            color: {current_theme['text_primary']};
            padding: 1.5rem;
            border-left: 4px solid {current_theme['accent']};
            border-radius: 0.8rem;
            margin: 1rem 0;">
    <h3 style="color: {current_theme['accent']};">Card Title</h3>
    <p>Card content goes here</p>
</div>
""", unsafe_allow_html=True)
```
