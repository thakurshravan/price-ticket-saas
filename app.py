import streamlit as st
import pandas as pd
import qrcode
import io
import base64

st.set_page_config(page_title="Custom Bulk Label Generator", layout="wide")

if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# --- GLOBAL UTILITY LOGIC ---
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_qr_base64(url):
    if pd.isna(url) or not str(url).strip():
        url = "https://example.com"
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(str(url))
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

def get_custom_currency_svg(color_hex, size_px=24):
    return f"""
    <svg width="{size_px}px" height="{size_px}px" viewBox="0 0 200 200" style="display: block; overflow: visible;" xmlns="http://www.w3.org/2000/svg">
        <path d="M40 20 C 80 20, 110 30, 130 60 C 145 80, 150 105, 150 130 C 150 155, 140 170, 125 180 C 105 192, 70 195, 40 195 L 40 180 C 70 180, 95 175, 110 165 C 122 155, 128 142, 128 125 C 128 105, 122 88, 108 75 C 92 60, 68 55, 40 55 Z" fill="{color_hex}"/>
        <path d="M20 80 L 175 80 C 185 80, 190 88, 185 95 C 180 102, 170 102, 160 102 L 20 102 C 10 102, 5 95, 10 88 C 15 82, 20 80, 20 80 Z" fill="{color_hex}"/>
        <path d="M20 115 L 175 115 C 185 115, 190 123, 185 130 C 180 137, 170 137, 160 137 L 20 137 C 10 137, 5 130, 10 123 C 15 117, 20 115, 20 115 Z" fill="{color_hex}"/>
    </svg>
    """

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("🎨 Advanced Customization Engine")

SIZE_TEMPLATES = {
    "60x40 mm (Standard Shelf Edge)": {"w": 60, "h": 40, "qr_size": 14},
    "40x50 mm (Hang Tag)": {"w": 40, "h": 50, "qr_size": 12},
    "80x50 mm (Large Display)": {"w": 80, "h": 50, "qr_size": 18},
    "Custom Size...": None
}

selected_size = st.sidebar.selectbox("1. Select Target Ticket Size", list(SIZE_TEMPLATES.keys()))

if selected_size == "Custom Size...":
    st.sidebar.markdown("📐 **Enter Manual Dimensions (in mm):**")
    custom_w = st.sidebar.number_input("Ticket Width (mm)", min_value=10, max_value=250, value=60, step=1)
    custom_h = st.sidebar.number_input("Ticket Height (mm)", min_value=10, max_value=250, value=40, step=1)
    custom_qr = st.sidebar.number_input("QR Code Size (mm)", min_value=5, max_value=min(custom_w, custom_h)-5, value=14, step=1)
    dimensions = {"w": custom_w, "h": custom_h, "qr_size": custom_qr}
else:
    dimensions = SIZE_TEMPLATES[selected_size]

primary_color = st.sidebar.color_picker("Text & Accent Color", "#8a1515")

bg_style = st.sidebar.selectbox("Ticket Background Style", [
    "Solid Accent Header",
    "Plain White", 
    "Light Border Box", 
    "Minimalist Left Ribbon", 
    "Modern Gradient Top", 
    "Double Thin Border",
    "Soft Cream Vintage", 
    "Dark Mode Luxury"
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
    
    if style_name == "Solid Accent Header":
        card_border = f"2px solid {primary_hex}"
        header_bg = primary_hex
        header_text = "#ffffff"
    elif style_name == "Light Border Box":
        card_border = f"2px solid {primary_hex}"
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

    return {
        "card_bg": card_bg, "card_border": card_border, "header_bg": header_bg, 
        "header_text": header_text, "left_ribbon": left_ribbon_html
    }

styles = compute_ticket_styles(bg_style, primary_color)

active_text_color = "#ffffff" if bg_style == "Dark Mode Luxury" else primary_color
code_text_color = "#aaaaaa" if bg_style == "Dark Mode Luxury" else "#555555"
preview_canvas_bg = styles["card_bg"]

# --- MAIN INTERFACE LAYOUT ---
st.title("🎟️ Custom Bulk Price Ticket Generator")
st.write("Upload a product template file, customize layout properties, and trigger local hardware prints.")

# --- LIVE PREVIEW WINDOW ---
st.subheader("👀 Live Ticket Sample Preview")

main_icon_size = max(18, int((price_size + 4) * 0.85))
was_icon_size = max(13, int((price_size - 4) * 0.85))

preview_price_table_html = f"""
<table style="border-collapse: collapse; border: none; margin: 0; padding: 0;">
    <tbody>
"""
if show_was_price:
    preview_price_table_html += f"""
        <tr>
            <td style="padding: 0 4px 0 0; margin: 0; vertical-align: middle; line-height: 1;">{get_custom_currency_svg("#888", size_px=was_icon_size)}</td>
            <td style="padding: 0; margin: 0; vertical-align: middle; line-height: 1; font-size: {price_size - 4}px; color: #888; text-decoration: line-through;">90.85</td>
        </tr>
    """
preview_price_table_html += f"""
        <tr>
            <td style="padding: 0 4px 0 0; margin: 0; vertical-align: middle; line-height: 1;">{get_custom_currency_svg(active_text_color, size_px=main_icon_size)}</td>
            <td style="padding: 0; margin: 0; vertical-align: middle; line-height: 1; font-size: {price_size + 4}px; font-weight: bold; color: {active_text_color};">79.00</td>
        </tr>
    </tbody>
</table>
"""

preview_logo_html = ""
if logo_b64:
    preview_logo_html = f"""
    <div style="position: absolute; top: 6px; right: 8px; max-width: 30%; max-height: 35%; display: flex; justify-content: flex-end; align-items: center; z-index: 20;">
        <img src="data:image/png;base64,{logo_b64}" style="max-width: 100%; max-height: 100%; object-fit: contain;" />
    </div>
    """

double_border_inset_open = f'<div style="position: absolute; top: 3px; bottom: 3px; left: 3px; right: 3px; border: 1px solid {primary_color}; box-sizing: border-box; pointer-events: none;">' if bg_style == "Double Thin Border" else ""
double_border_inset_close = '</div>' if bg_style == "Double Thin Border" else ""

preview_code_above_qr_html = f"""
<div style="position: absolute; bottom: calc(10px + {dimensions['qr_size'] * 4}px + 6px); right: 8px; font-weight: bold; font-size: 11px; text-align: center; color: {code_text_color}; z-index: 10;">
    1011480
</div>
"""

preview_html = f"""
<div style="
    width: {dimensions['w'] * 4}px; 
    height: {dimensions['h'] * 4}px; 
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
    {preview_logo_html}
    
    <div style="background: {styles['header_bg']}; padding: 8px; padding-right: 35%; height: 35%; box-sizing: border-box;">
        <div style="color: {styles['header_text']}; font-size: {title_size + 4}px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            <strong style="text-transform: uppercase;">HYPHEN</strong>: MagSafe AIRE Clear Case for iPhone 13, Clear
        </div>
    </div>
    <div style="position: absolute; top: 41%; left: {'14px' if bg_style == 'Minimalist Left Ribbon' else '8px'}; color: {code_text_color}; font-size: 11px; font-weight: bold;">
        ITEM CODE: 1011480
    </div>
    
    <div style="position: absolute; bottom: 10px; left: {'14px' if bg_style == 'Minimalist Left Ribbon' else '8px'};">
        {preview_price_table_html}
    </div>
    
    {preview_code_above_qr_html}
    <div style="position: absolute; bottom: 10px; right: 8px; width: {dimensions['qr_size'] * 4}px; height: {dimensions['qr_size'] * 4}px; background-image: url('data:image/png;base64,{generate_qr_base64("https://example.com")}'); background-size: cover; border: 1px solid #eee;"></div>
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
            data_str = file_bytes.decode('utf-8-sig', errors='ignore')
            df = pd.read_csv(io.StringIO(data_str))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
        
        df.columns = df.columns.astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        df = df.dropna(how='all')
        
        mapped_cols = {}
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            if "sku" in col_lower or "barcode" in col_lower or "item code" in col_lower:
                mapped_cols["SKU"] = col
            elif "product" in col_lower or "name" in col_lower or "title" in col_lower or "description" in col_lower:
                mapped_cols["Product Name"] = col
            elif col_lower == "now" or "price" in col_lower or "retail" in col_lower or "selling" in col_lower:
                mapped_cols["Price"] = col
            elif col_lower == "was" or "old" in col_lower or "strike" in col_lower:
                mapped_cols["Was Price"] = col
            elif "brand" in col_lower:
                mapped_cols["Brand"] = col
            elif "url" in col_lower or "link" in col_lower or "website" in col_lower:
                mapped_cols["URL"] = col

        if "URL" not in mapped_cols:
            df["Generated_URL"] = "https://example.com"
            mapped_cols["URL"] = "Generated_URL"

        required_targets = ["SKU", "Product Name", "Price"]
        missing_targets = [t for t in required_targets if t not in mapped_cols]
        
        if missing_targets:
            st.error(f"Execution Halted. Missing columns: {missing_targets}")
            st.write("Detected Columns in your file:", list(df.columns))
        else:
            st.success("✨ Data payload mapped successfully!")
            st.dataframe(df.head(3), use_container_width=True)

            # --- GENERATION ENGINE ---
            html_cards = ""
            for idx, row in df.iterrows():
                try:
                    price_val = float(row[mapped_cols["Price"]])
                    formatted_num = f"{price_val:.2f}"
                except:
                    formatted_num = str(row[mapped_cols['Price']])

                was_formatted_num = ""
                if "Was Price" in mapped_cols and not pd.isna(row[mapped_cols["Was Price"]]):
                    try:
                        was_val = float(row[mapped_cols["Was Price"]])
                        was_formatted_num = f"{was_val:.2f}"
                    except:
                        was_formatted_num = str(row[mapped_cols["Was Price"]])

                brand_val = ""
                if "Brand" in mapped_cols and not pd.isna(row[mapped_cols["Brand"]]):
                    brand_val = str(row[mapped_cols["Brand"]]).strip()

                item_code_val = str(row[mapped_cols["SKU"]]).strip()
                target_url = row[mapped_cols["URL"]]
                qr_b64 = generate_qr_base64(target_url)

                print_main_icon_size = max(16, int(price_size * 0.85))
                print_was_icon_size = max(11, int((price_size - 4) * 0.85))

                print_price_table_html = f"""
                <table style="border-collapse: collapse; border: none; margin: 0; padding: 0;">
                    <tbody>
                """
                if show_was_price and was_formatted_num:
                    print_price_table_html += f"""
                        <tr>
                            <td style="padding: 0 4px 0 0; margin: 0; vertical-align: middle; line-height: 1;">{get_custom_currency_svg("#888", size_px=print_was_icon_size)}</td>
                            <td style="padding: 0; margin: 0; vertical-align: middle; line-height: 1; font-size: {price_size - 4}pt; color: #888; text-decoration: line-through;">{was_formatted_num}</td>
                        </tr>
                    """
                print_price_table_html += f"""
                        <tr>
                            <td style="padding: 0 4px 0 0; margin: 0; vertical-align: middle; line-height: 1;">{get_custom_currency_svg(active_text_color, size_px=print_main_icon_size)}</td>
                            <td style="padding: 0; margin: 0; vertical-align: middle; line-height: 1; font-size: {price_size}pt; font-weight: bold; color: {active_text_color};">{formatted_num}</td>
                        </tr>
                    </tbody>
                </table>
                """

                card_logo_html = ""
                if logo_b64:
                    card_logo_html = f"""
                    <div style="position: absolute; top: 1.5mm; right: 2mm; max-width: 30%; max-height: 35%; display: flex; justify-content: flex-end; align-items: center; z-index: 20;">
                        <img src="data:image/png;base64,{logo_b64}" style="max-width: 100%; max-height: 100%; object-fit: contain;" />
                    </div>
                    """

                print_double_border_open = f'<div style="position: absolute; top: 0.8mm; bottom: 0.8mm; left: 0.8mm; right: 0.8mm; border: 0.25mm solid {primary_color}; box-sizing: border-box; pointer-events: none;">' if bg_style == "Double Thin Border" else ""
                print_double_border_close = '</div>' if bg_style == "Double Thin Border" else ""

                print_code_above_qr_html = f"""
                <div style="position: absolute; bottom: calc(4px + {dimensions['qr_size']}mm + 1.5mm); right: 4px; font-weight: bold; font-size: 8pt; text-align: center; color: {code_text_color}; z-index: 10;">
                    {item_code_val}
                </div>
                """

                title_header_content = f'{row[mapped_cols["Product Name"]]}'
                if brand_val:
                    title_header_content = f'<strong style="text-transform: uppercase;">{brand_val}</strong>: {title_header_content}'

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
                    {card_logo_html}
                    
                    <div style="background: {styles['header_bg']}; padding: 6px; padding-right: 35%; height: 35%; box-sizing: border-box;">
                        <div style="color: {styles['header_text']}; font-size: {title_size}pt; line-height: 1.1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {title_header_content}
                        </div>
                    </div>
                    <div style="position: absolute; top: 42%; left: {'5mm' if bg_style == 'Minimalist Left Ribbon' else '6px'}; color: {code_text_color}; font-size: 8pt; font-weight: bold;">
                        ITEM CODE: {item_code_val}
                    </div>
                    
                    <div style="position: absolute; bottom: 6px; left: {'5mm' if bg_style == 'Minimalist Left Ribbon' else '6px'};">
                        {print_price_table_html}
                    </div>
                    
                    {print_code_above_qr_html}
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
