"""
Centralized Theme Configuration for AI Trip Agent UI

This module provides a unified theme system for both the main app and observability dashboard.
All color schemes and styling configurations are defined here to ensure consistency.

Usage:
    from styles.theme import THEMES, get_theme_css
    
    # In your Streamlit app:
    current_theme = THEMES[st.session_state.theme]
    st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

Modifying Themes:
    1. Edit the THEMES dictionary below to change colors
    2. Colors are defined in hex format (e.g., "#ffffff")
    3. Both 'light' and 'dark' themes must have the same keys
    4. After modifying, restart your Streamlit app to see changes

Theme Structure:
    - bg_primary: Main background color
    - bg_secondary: Secondary background (cards, containers)
    - bg_sidebar: Sidebar background
    - text_primary: Primary text color
    - text_secondary: Secondary/muted text color
    - accent: Accent color for highlights and primary actions
    - success: Success state color (green)
    - warning: Warning state color (orange)
    - danger: Error/danger state color (red)
    - user_msg: User message background
    - assistant_msg: Assistant message background
    - border: Border color
    - button_bg: Primary button background
    - button_text: Button text color
    - action_button: Action button color
    - danger_button: Danger button color
"""

# Theme color definitions
THEMES = {
    "light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f0f2f6",
        "bg_sidebar": "#f8f9fa",
        "text_primary": "#1f1f1f",
        "text_secondary": "#4a4a4a",
        "accent": "#1976d2",
        "success": "#2e7d32",
        "warning": "#f57c00",
        "danger": "#d32f2f",
        "user_msg": "#e3f2fd",
        "assistant_msg": "#e8f5e9",
        "border": "#dee2e6",
        "button_bg": "#1976d2",
        "button_text": "#ffffff",
        "action_button": "#f57c00",
        "danger_button": "#d32f2f",
    },
    "dark": {
        "bg_primary": "#0e1117",
        "bg_secondary": "#262730",
        "bg_sidebar": "#1a1d24",
        "text_primary": "#fafafa",
        "text_secondary": "#b0b0b0",
        "accent": "#42a5f5",
        "success": "#66bb6a",
        "warning": "#ffa726",
        "danger": "#ef5350",
        "user_msg": "#1e3a5f",
        "assistant_msg": "#1a3a1a",
        "border": "#404040",
        "button_bg": "#42a5f5",
        "button_text": "#ffffff",
        "action_button": "#ffa726",
        "danger_button": "#ef5350",
    }
}


def get_base_css(theme: dict) -> str:
    """
    Generate base CSS that applies to all pages.
    
    Args:
        theme: Theme dictionary with color definitions
        
    Returns:
        CSS string with base styles
    """
    return f"""
    <style>
        /* Global app background */
        .stApp {{
            background-color: {theme['bg_primary']} !important;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {theme['bg_sidebar']} !important;
        }}
        
        /* Sidebar text - ensure visibility in both themes */
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] h5,
        [data-testid="stSidebar"] h6 {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Button styling - CRITICAL for visibility */
        .stButton > button {{
            background-color: {theme['button_bg']} !important;
            color: {theme['button_text']} !important;
            border: none !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background-color: {theme['accent']}dd !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
            transform: translateY(-2px) !important;
        }}
        
        /* Sidebar buttons - ensure they're visible */
        [data-testid="stSidebar"] .stButton > button {{
            background-color: {theme['button_bg']} !important;
            color: {theme['button_text']} !important;
        }}
        
        /* Header buttons (theme toggle, navigation) */
        [data-testid="stMainBlockContainer"] > div:first-child .stButton > button {{
            background-color: {theme['button_bg']} !important;
            color: {theme['button_text']} !important;
        }}
        
        /* Select boxes */
        [data-baseweb="select"] {{
            background-color: {theme['bg_secondary']} !important;
        }}
        
        [data-baseweb="select"] > div {{
            background-color: {theme['bg_secondary']} !important;
            color: {theme['text_primary']} !important;
        }}
        
        /* Dropdown menu */
        [data-baseweb="menu"] {{
            background-color: {theme['bg_secondary']} !important;
        }}
        
        [data-baseweb="menu"] * {{
            color: {theme['text_primary']} !important;
            background-color: {theme['bg_secondary']} !important;
        }}
        
        /* Dropdown list items */
        [role="option"] {{
            background-color: {theme['bg_secondary']} !important;
            color: {theme['text_primary']} !important;
        }}
        
        [role="option"]:hover {{
            background-color: {theme['accent']}33 !important;
        }}
        
        /* Input fields */
        input, textarea, select {{
            background-color: {theme['bg_secondary']} !important;
            color: {theme['text_primary']} !important;
        }}
        
        /* Checkbox and radio labels */
        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Slider labels */
        [data-testid="stSlider"] label {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Main content headers */
        [data-testid="stMainBlockContainer"] h1,
        [data-testid="stMainBlockContainer"] h2,
        [data-testid="stMainBlockContainer"] h3,
        [data-testid="stMainBlockContainer"] h4,
        [data-testid="stMainBlockContainer"] h5,
        [data-testid="stMainBlockContainer"] h6 {{
            color: {theme['text_primary']} !important;
        }}
        
        /* Fix for header */
        [data-testid="stHeader"] {{
            background-color: {theme['bg_primary']} !important;
        }}

        /* Fix for header toolbar buttons (stop, deploy, menu) */
        [data-testid="stHeader"] button {{
            background-color: {theme['button_bg']} !important;
            color: {theme['button_text']} !important;
            border: 1px solid {theme['border']} !important;
        }}

        [data-testid="stHeader"] button:hover {{
            background-color: {theme['accent']} !important;
            opacity: 0.9 !important;
        }}

        /* Fix for header toolbar icons */
        [data-testid="stHeader"] svg {{
            color: {theme['text_primary']} !important;
            fill: {theme['text_primary']} !important;
            stroke: {theme['text_primary']} !important;
        }}

        /* Fix for header menu button (three dots) */
        [data-testid="stHeader"] [data-testid="stActionButton"] button {{
            background-color: {theme['button_bg']} !important;
            color: {theme['button_text']} !important;
            border: none !important;
            padding: 6px !important;
        }}

        /* Fix for bottom block container */
        [data-testid="stBottomBlockContainer"] {{
            background-color: {theme['bg_primary']} !important;
        }}
    </style>
    """


def get_main_app_css(theme: dict) -> str:
    """
    Generate CSS specific to the main app (streamlit_app.py).

    Args:
        theme: Theme dictionary with color definitions

    Returns:
        CSS string with main app specific styles
    """
    return f"""
    <style>
        /* Headers */
        .main-header {{
            font-size: 2.8rem;
            font-weight: 800;
            color: {theme['accent']};
            text-align: center;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}

        .sub-header {{
            font-size: 1.3rem;
            color: {theme['text_secondary']};
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 300;
        }}

        /* Chat input styling */
        .stChatInput {{
            background-color: {theme['bg_secondary']} !important;
            border-radius: 0.6rem;
            padding: 0.4rem;
            border: 1px solid {theme['border']};
        }}

        .stChatInput input, .stChatInput textarea {{
            background-color: {theme['bg_secondary']} !important;
            color: {theme['text_primary']} !important;
            border: none !important;
            outline: none !important;
            width: 100%;
            font-size: 0.95rem;
            padding: 0.5rem;
        }}

        /* Ensure card, container and block backgrounds are visible */
        .stBlock, .stMarkdown, .stExpander {{
            background-color: {theme['bg_primary']} !important;
            color: {theme['text_primary']} !important;
        }}

        /* Action buttons styling */
        .action-button-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
            padding: 0.75rem;
            background-color: {theme['bg_secondary']};
            border-radius: 0.8rem;
            border: 1px solid {theme['border']};
            align-items: center;
        }}

        .action-button {{
            background-color: {theme['accent']};
            color: {theme['text_primary']};
            padding: 0.5rem 0.9rem;
            border-radius: 0.6rem;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.15s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}

        .action-button.secondary {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_secondary']};
            border: 1px solid {theme['border']};
        }}

        .action-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}

        .action-button:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        }}

        /* Message boxes */
        .message-user {{
            background: linear-gradient(135deg, {theme['user_msg']} 0%%, {theme['user_msg']}dd 100%%);
            color: {theme['text_primary']};
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            border-left: 5px solid {theme['accent']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .message-assistant {{
            background: linear-gradient(135deg, {theme['assistant_msg']} 0%%, {theme['assistant_msg']}dd 100%%);
            color: {theme['text_primary']};
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            border-left: 5px solid {theme['success']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .message-agent {{
            background: linear-gradient(135deg, {theme['warning']}33 0%%, {theme['warning']}22 100%%);
            color: {theme['text_primary']};
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            border-left: 5px solid {theme['warning']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        /* Response content */
        .response-content {{
            color: {theme['text_primary']};
            line-height: 1.8;
            white-space: pre-wrap;
            font-size: 1rem;
        }}

        /* Info boxes */
        .carbon-box {{
            background-color: {theme['success']}22;
            color: {theme['text_primary']};
            padding: 1.2rem;
            border-radius: 0.8rem;
            border-left: 4px solid {theme['success']};
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .itinerary-box {{
            background-color: {theme['warning']}22;
            color: {theme['text_primary']};
            padding: 1.5rem;
            border-radius: 0.8rem;
            margin: 1rem 0;
            border-left: 4px solid {theme['warning']};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .agent-status-box {{
            background-color: {theme['accent']}22;
            color: {theme['text_primary']};
            padding: 1.2rem;
            border-radius: 0.8rem;
            border: 2px solid {theme['accent']};
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* Option cards */
        .option-card {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            padding: 1rem;
            border-radius: 0.8rem;
            border: 2px solid {theme['border']};
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .option-card:hover {{
            border-color: {theme['accent']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }}
    </style>
    """


def get_observability_css(theme: dict) -> str:
    """
    Generate CSS specific to the observability dashboard.
    
    Args:
        theme: Theme dictionary with color definitions
        
    Returns:
        CSS string with observability dashboard specific styles
    """
    return f"""
    <style>
        /* Metric cards */
        .metric-card {{
            background: linear-gradient(135deg, {theme['bg_secondary']} 0%%, {theme['bg_primary']} 100%%);
            padding: 1.5rem;
            border-radius: 1rem;
            border: 2px solid {theme['accent']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 1rem 0;
        }}

        .metric-card h3,
        .metric-card p {{
            color: {theme['text_primary']} !important;
        }}

        /* Agent cards */
        .agent-card {{
            background: {theme['bg_secondary']};
            padding: 1.2rem;
            border-radius: 0.8rem;
            border-left: 4px solid {theme['success']};
            margin: 0.8rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .agent-card p,
        .agent-card strong {{
            color: {theme['text_primary']} !important;
        }}

        /* Trace cards */
        .trace-card {{
            background: {theme['bg_secondary']};
            padding: 1rem;
            border-radius: 0.8rem;
            border-left: 4px solid {theme['accent']};
            margin: 0.5rem 0;
        }}

        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 1rem;
            font-weight: 600;
            font-size: 0.85rem;
        }}

        .status-active {{
            background-color: {theme['success']}33;
            color: {theme['success']};
        }}

        .status-stopped {{
            background-color: {theme['text_secondary']}33;
            color: {theme['text_secondary']};
        }}

        .status-error {{
            background-color: {theme['danger']}33;
            color: {theme['danger']};
        }}

        /* Fix Streamlit alert boxes (warning, info, success, error) */
        [data-testid="stAlert"] {{
            background-color: {theme['bg_secondary']} !important;
            border-color: {theme['border']} !important;
        }}

        /* Fix all text inside alert boxes */
        [data-testid="stAlert"],
        [data-testid="stAlert"] *,
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] span,
        [data-testid="stAlert"] div,
        [data-testid="stAlert"] strong,
        [data-testid="stAlert"] em,
        [data-testid="stAlert"] li,
        [data-testid="stAlert"] ol,
        [data-testid="stAlert"] ul {{
            color: {theme['text_primary']} !important;
        }}

        /* Fix markdown content in alerts */
        [data-testid="stAlert"] [data-testid="stMarkdown"],
        [data-testid="stAlert"] [data-testid="stMarkdown"] *,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {{
            color: {theme['text_primary']} !important;
        }}

        /* Fix links in alerts */
        [data-testid="stAlert"] a {{
            color: {theme['accent']} !important;
        }}

        /* Fix code blocks in alerts */
        [data-testid="stAlert"] code,
        [data-testid="stAlert"] pre {{
            background-color: {theme['bg_primary']} !important;
            color: {theme['accent']} !important;
            border: 1px solid {theme['border']} !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 0.3rem !important;
        }}

        /* Fix inline code */
        [data-testid="stAlert"] code {{
            background-color: {theme['bg_primary']} !important;
            color: {theme['accent']} !important;
        }}

        /* Fix code blocks globally */
        code, pre {{
            background-color: {theme['bg_secondary']} !important;
            color: {theme['accent']} !important;
            border: 1px solid {theme['border']} !important;
        }}

        /* Fix code block content */
        pre code {{
            background-color: transparent !important;
            color: {theme['text_primary']} !important;
        }}
        [data-testid="stAlert"] pre {{
            background-color: {theme['bg_primary']} !important;
            color: {theme['text_primary']} !important;
            border: 1px solid {theme['border']} !important;
        }}

        /* Fix all markdown text globally */
        [data-testid="stMarkdown"],
        [data-testid="stMarkdown"] *,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] * {{
            color: {theme['text_primary']} !important;
        }}

        /* Fix numbered and bulleted lists */
        ol, ul, li {{
            color: {theme['text_primary']} !important;
        }}

        /* Fix all paragraph text */
        p {{
            color: {theme['text_primary']} !important;
        }}
    </style>
    """


def get_theme_css(theme: dict, page_type: str = "main") -> str:
    """
    Get complete CSS for a specific page.
    
    Args:
        theme: Theme dictionary with color definitions
        page_type: Type of page ("main" or "observability")
        
    Returns:
        Complete CSS string for the page
    """
    base = get_base_css(theme)
    
    if page_type == "main":
        return base + get_main_app_css(theme)
    elif page_type == "observability":
        return base + get_observability_css(theme)
    else:
        return base
