import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Генератор этикеток", layout="centered")

st.title("Генератор сетки штрихкодов 2х4")
st.write("Сетка 8 штук на этикетку 75х120 мм")

uploaded_file = st.file_uploader("Загрузите PDF файл", type=["pdf"])
copies = st.number_input("Сколько копий каждого штрихкода сделать?", min_value=1, value=1, step=1)

if uploaded_file is not None:
    if st.button("Сформировать PDF"):
        # Размеры в pt (75x120 мм)
        page_w, page_h = 75 * 2.83465, 120 * 2.83465
        cols, rows = 2, 4
        cell_w, cell_h = page_w / cols, page_h / rows
        
        src_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        all_pages = []
        for page_num in range(len(src_doc)):
            for _ in range(int(copies)):
                all_pages.append(page_num)
                
        out_doc = fitz.open()
        total_items = len(all_pages)
        
        for i in range(0, total_items, 8):
            chunk = all_pages[i:i + 8]
            out_page = out_doc.new_page(width=page_w, height=page_h)
            
            for idx, src_page_idx in enumerate(chunk):
                r = idx // cols
                c = idx % cols
                x0, y0 = c * cell_w, r * cell_h
                x1, y1 = x0 + cell_w, y0 + cell_h
                rect = fitz.Rect(x0, y0, x1, y1)
                out_page.show_pdf_page(rect, src_doc, src_page_idx)
                
        pdf_bytes = out_doc.tobytes()
        
        st.success("Готово!")
        st.download_button(
            label="Скачать готовый PDF (75х120 мм)",
            data=pdf_bytes,
            file_name="result_75x120.pdf",
            mime="application/pdf"
        )
