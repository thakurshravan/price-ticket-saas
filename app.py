import streamlit as st
import pandas as pd
import qrcode
import io
import base64

st.set_page_config(page_title="SaaS Bulk Label Generator", layout="wide")

if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# --- GLOBAL UTILITY LOGIC ---
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_qr_base64(url):
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def process_logo_to_base64(uploaded_logo):
    if uploaded_logo is not None:
        try:
            bytes_data = uploaded_logo.getvalue()
            return base64.b64encode(bytes_data).decode()
        except:
            return None
    return None

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("🎨 Advanced Customization Engine")

SIZE_TEMPLATES = {
    "60x40 mm (Standard Shelf Edge)": {"w": 60, "h": 40, "qr_size": 18},
    "40x50 mm (Hang Tag)": {"w": 40, "h": 50, "qr_size": 15},
    "80x50 mm (Large Display)": {"w": 80, "h": 50, "qr_size": 22},
    "A5 Size (148x210 mm)": {"w": 148, "h": 210, "qr_size": 45},
    "A6 Size (105x148 mm)": {"w": 105, "h": 148, "qr_size": 35},
    "A7 Size (74x105 mm)": {"w": 74, "h": 105, "qr_size": 25},
    "Custom Size...": None
}

selected_size = st.sidebar.selectbox("1. Select Target Ticket Size", list(SIZE_TEMPLATES.keys()))

if selected_size == "Custom Size...":
    st.sidebar.markdown("📐 **Enter Manual Dimensions (in mm):**")
    custom_w = st.sidebar.number_input("Ticket Width (mm)", min_value=10, max_value=250, value=60, step=1)
    custom_h = st.sidebar.number_input("Ticket Height (mm)", min_value=10, max_value=250, value=40, step=1)
    custom_qr = st.sidebar.number_input("QR Code Size (mm)", min_value=5, max_value=min(custom_w, custom_h)-5, value=18, step=1)
    dimensions = {"w": custom_w, "h": custom_h, "qr_size": custom_qr}
else:
    dimensions = SIZE_TEMPLATES[selected_size]

primary_color = st.sidebar.color_picker("Text & Accent Color", "#1E1E1E")

bg_style = st.sidebar.selectbox("Ticket Background Style", [
    "Plain White", 
    "Light Border Box", 
    "Solid Accent Header", 
    "Minimalist Left Ribbon", 
    "Modern Gradient Top", 
    "Double Thin Border",
    "Soft Cream Vintage", 
    "Dark Mode Luxury", 
    "Diagonal Corner Accent",
    "Bottom Accent Footer"
])

st.sidebar.subheader("Typography")
font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size", 8, 24, 11)
price_size = st.sidebar.slider("Price Font Size", 14, 42, 18)

show_was_price = st.sidebar.checkbox("Show Strikethrough 'Was' Price Row", value=True)

st.sidebar.subheader("🏢 Corporate Branding")
uploaded_logo = st.sidebar.file_uploader("Upload Brand Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
logo_b64 = process_logo_to_base64(uploaded_logo)

# --- GLOBAL FONT CONFIGURATION ---
web_font = "Courier New, monospace" if font_choice == "Courier" else f"{font_choice}, sans-serif"

# --- CORE STYLE SOLVER LOGIC ---
def compute_ticket_styles(style_name, primary_hex):
    card_bg = "#ffffff"
    card_border = "1px dashed #ccc"
    header_bg = "transparent"
    header_text = primary_hex
    left_ribbon_html = ""
    corner_accent_html = ""
    footer_bg_html = ""
    
    if style_name == "Light Border Box":
        card_border = f"2px solid {primary_hex}"
    elif style_name == "Solid Accent Header":
        card_border = f"2px solid {primary_hex}"
        header_bg = primary_hex
        header_text = "#ffffff"
    elif style_name == "Minimalist Left Ribbon":
        card_border = "1px solid #e0e0e0"
        left_ribbon_html = f'<div style="position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background-color: {primary_hex};"></div>'
    elif style_name == "Modern Gradient Top":
        card_border = "1px solid #e0e0e0"
        header_bg = f"linear-gradient(135deg, {primary_hex} 0%, #4f4f4f 100%)"
        header_text = "#ffffff"
    elif style_name == "Double Thin Border":
        card_border = f"1px solid {primary_hex}"
    elif style_name == "Soft Cream Vintage":
        card_bg = "#fdfbf7"
        card_border = "2px solid #dcd1bd"
        header_text = primary_hex
    elif style_name == "Dark Mode Luxury":
        card_bg = "#121212"
        card_border = "1px solid #2d2d2d"
        header_bg = "#1a1a1a"
        header_text = "#ffffff"
    elif style_name == "Diagonal Corner Accent":
        card_border = "1px solid #e0e0e0"
        corner_accent_html = f'<div style="position: absolute; right: -25px; top: -25px; width: 50px; height: 50px; background-color: {primary_hex}; transform: rotate(45deg); z-index: 10;"></div>'
    elif style_name == "Bottom Accent Footer":
        card_border = "1px solid #e0e0e0"
        footer_bg_html = f'<div style="position: absolute; bottom: 0; left: 0; right: 0; height: 6px; background-color: {primary_hex};"></div>'

    return {
        "card_bg": card_bg, "card_border": card_border, "header_bg": header_bg, 
        "header_text": header_text, "left_ribbon": left_ribbon_html, 
        "corner_accent": corner_accent_html, "footer_bg": footer_bg_html
    }

styles = compute_ticket_styles(bg_style, primary_color)

active_text_color = "#ffffff" if bg_style == "Dark Mode Luxury" else primary_color
sku_text_color = "#aaaaaa" if bg_style == "Dark Mode Luxury" else "#555555"
preview_canvas_bg = styles["card_bg"]

# --- MAIN INTERFACE LAYOUT ---
st.title("🎟️ Custom SaaS Bulk Price Ticket Generator")
st.write("Upload a file, customize styles, and print directly onto standard A4 sticker sheets.")

# --- LIVE PREVIEW WINDOW ---
st.subheader("👀 Live Ticket Sample Preview")
# Swapped AED out for the traditional Arabic د.إ sign
was_price_html = f'<div style="text-decoration: line-through; font-size: {price_size - 4}pt; color: #888; line-height: 1; direction: rtl; text-align: left;">789.00 د.إ</div>' if show_was_price else ''

preview_logo_html = ""
if logo_b64:
    preview_logo_html = f"""
    <img src="data:image/png;base64,{logo_b64}" style="
        position: absolute;
        top: 42%;
        right: 12px;
        max-height: 25px;
        max-width: 70px;
        object-fit: contain;
    " />
    """

double_border_inset_open = f'<div style="position: absolute; top: 3px; bottom: 3px; left: 3px; right: 3px; border: 1px solid {primary_color}; box-sizing: border-box; pointer-events: none;">' if bg_style == "Double Thin Border" else ""
double_border_inset_close = '</div>' if bg_style == "Double Thin Border" else ""

preview_html = f"""
<div style="
    width: {dimensions['w'] * 3}px; 
    height: {dimensions['h'] * 3}px; 
    border: {styles['card_border']}; 
    background: {preview_canvas_bg}; 
    border-radius: 4px; 
    position: relative; 
    font-family: {web_font}; 
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    margin-bottom: 20px;
">
    {double_border_inset_open}
    {styles['left_ribbon']}
    {styles['corner_accent']}
    {styles['footer_bg']}
    
    <div style="background: {styles['header_bg']}; padding: 8px; height: 35%; box-sizing: border-box;">
        <div style="color: {styles['header_text']}; font-size: {title_size + 4}px; font-weight: bold; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            Sample Product Name
        </div>
    </div>
    <div style="position: absolute; top: 45%; left: {'14px' if bg_style == 'Minimalist Left Ribbon' else '8px'}; color: {sku_text_color}; font-size: 11px;">
        SKU: J705466
    </div>
    
    {preview_logo_html}
    
    <div style="position: absolute; bottom: 10px; left: {'14px' if bg_style == 'Minimalist Left Ribbon' else '8px'}; line-height: 1;">
        {was_price_html}
        <div style="color: {active_text_color}; font-size: {price_size + 4}px; font-weight: bold; direction: rtl; text-align: left;">
            799.00 د.إ
        </div>
    </div>
    
    <div style="position: absolute; bottom: 10px; right: 8px; width: {dimensions['qr_size'] * 2.8}px; height: {dimensions['qr_size'] * 2.8}px; background-image: url('https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_QR_Code_tutorial_images_section.png'); background-size: cover; border: 1px solid #eee;"></div>
    {double_border_inset_close}
</div>
"""
st.markdown(preview_html, unsafe_allow_html=True)
st.divider()

# --- DATA IMPORT ENGINE ---
def clear_file_callback():
    st.session_state["file_uploader_key"] += 1

uploaded_file = st.file_uploader(
    "Upload Product File (.xlsx or .csv)", 
    type=["xlsx", "csv"], 
    key=f"file_uploader_{st.session_state['file_uploader_key']}"
)

if uploaded_file is not None:
    if st.button("🗑️ Clear File & Reset Canvas", on_click=clear_file_callback):
        st.rerun()

    try:
        file_bytes = uploaded_file.getvalue()
        if uploaded_file.name.endswith('.csv'):
            data_str = file_bytes.decode('utf-8', errors='ignore')
            df = pd.read_csv(io.StringIO(data_str), header=None)
        else:
            df = pd.read_excel(io.BytesIO(file_bytes), header=None)
        
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df.columns = df.iloc[0].astype(str).str.strip()
        df = df[1:].reset_index(drop=True)
        
        mapped_cols = {}
        for col in df.columns:
            col_lower = str(col).lower()
            if "sku" in col_lower:
                mapped_cols["SKU"] = col
            elif "product" in col_lower or "name" in col_lower or "title" in col_lower:
                mapped_cols["Product Name"] = col
            elif "price" in col_lower or "rate" in col_lower or "mrp" in col_lower:
                mapped_cols["Price"] = col
            elif "url" in col_lower or "link" in col_lower or "website" in col_lower:
                mapped_cols["URL"] = col

        required_targets = ["SKU", "Product Name", "Price", "URL"]
        missing_targets = [t for t in required_targets if t not in mapped_cols]
        
        if missing_targets:
            st.error(f"Execution Halted. Missing columns: {missing_targets}")
        else:
            st.success("✨ Data payload mapped successfully!")
            st.dataframe(df.head(3), use_container_width=True)

            # --- GENERATION ENGINE ---
            html_cards = ""
            for idx, row in df.iterrows():
                try:
                    price_val = float(row[mapped_cols["Price"]])
                    price_text = f"{price_val:.2f} د.إ"
                    was_price_text = f"{price_val * 1.15:.2f} د.إ" 
                except:
                    price_text = f"{row[mapped_cols['Price']]} د.إ"
                    was_price_text = ""

                qr_b64 = generate_qr_base64(str(row[mapped_cols["URL"]]))
                was_row_inner = f'<div style="text-decoration: line-through; font-size: {price_size - 4}pt; color: #888; margin-bottom: 1px; direction: rtl; text-align: left;">{was_price_text}</div>' if (show_was_price and was_price_text) else ''

                card_logo_html = ""
                if logo_b64:
                    card_logo_html = f"""
                    <img src="data:image/png;base64,{logo_b64}" style="
                        position: absolute;
                        top: 42%;
                        right: 6px;
                        max-height: 6mm;
                        max-width: 18mm;
                        object-fit: contain;
                    " />
                    """

                print_double_border_open = f'<div style="position: absolute; top: 0.8mm; bottom: 0.8mm; left: 0.8mm; right: 0.8mm; border: 0.25mm solid {primary_color}; box-sizing: border-box; pointer-events: none;">' if bg_style == "Double Thin Border" else ""
                print_double_border_close = '</div>' if bg_style == "Double Thin Border" else ""

                html_cards += f"""
                <div class="ticket-card" style="
                    width: {dimensions['w']}mm;
                    height: {dimensions['h']}mm;
                    border: {styles['card_border']};
                    box-sizing: border-box;
                    position: relative;
                    background: {styles['card_bg']};
                    font-family: {web_font};
                    overflow: hidden;
                    display: inline-block;
                    margin: 1mm;
                    vertical-align: top;
                    text-align: left;
                ">
                    {print_double_border_open}
                    {styles['left_ribbon']}
                    {styles['corner_accent']}
                    {styles['footer_bg']}
                    
                    <div style="background: {styles['header_bg']}; padding: 6px; height: 35%; box-sizing: border-box;">
                        <div style="color: {styles['header_text']}; font-size: {title_size}pt; font-weight: bold; line-height: 1.1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {row[mapped_cols["Product Name"]]}
                        </div>
                    </div>
                    <div style="position: absolute; top: 42%; left: {'5mm' if bg_style == 'Minimalist Left Ribbon' else '6px'}; color: {sku_text_color}; font-size: 8pt;">
                        SKU: {row[mapped_cols["SKU"]]}
                    </div>
                    
                    {card_logo_html}
                    
                    <div style="position: absolute; bottom: 6px; left: {'5mm' if bg_style == 'Minimalist Left Ribbon' else '6px'}; line-height: 1;">
                        {was_row_inner}
                        <div style="color: {active_text_color}; font-size: {price_size}pt; font-weight: bold; direction: rtl; text-align: left;">
                            {price_text}
                        </div>
                    </div>
                    
                    <img src="data:image/png;base64,{qr_b64}" style="
                        position: absolute;
                        bottom: 4px;
                        right: 4px;
                        width: {dimensions['qr_size']}mm;
                        height: {dimensions['qr_size']}mm;
                    " />
                    {print_double_border_close}
                </div>
                """

            st.subheader("🖨️ Printable Document Feed")
            iframe_content = f"""
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; font-family: sans-serif; text-align: center; background: #fafafa; }}
                    .print-btn {{
                        background-color: #25d366; color: white; border: none; padding: 12px 30px;
                        font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 15px auto; display: block;
                    }}
                    .print-btn:hover {{ background-color: #1ebe57; }}
                    .a4-page {{
                        width: 210mm; padding: 5mm; margin: 0 auto;
                        background: white; box-sizing: border-box; text-align: left;
                    }}
                    @media print {{
                        .print-btn {{ display: none !important; }}
                        body {{ background: white; }}
                        .a4-page {{ padding: 0; margin: 0; width: 100%; }}
                    }}
                </style>
            </head>
            <body>
                <button class="print-btn" onclick="window.print()">🖨️ CLICK HERE TO PRINT BULK SHEET</button>
                <div class="a4-page">
                    {html_cards}
                </div>
            </body>
            </html>
            """
            st.components.v1.html(iframe_content, height=800, scrolling=True)

    except Exception as e:
        st.error(f"Fatal Parser Error: {e}")
