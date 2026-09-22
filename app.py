import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Генератор этикеток", layout="centered")

st.title("Генератор сетки штрихкодов")
st.write("Автоматическая раскладка на этикетку 75х120 мм")

uploaded_file = st.file_uploader("Загрузите PDF файл", type=["pdf"])

# Контейнер с гибкими настройками
with st.container():
    st.subheader("Настройки раскладки")
    
    copies = st.number_input(
        "Сколько копий каждого штрихкода сделать?", 
        min_value=1, 
        value=1, 
        step=1
    )
    
    st.write("---")
    st.markdown("**Настройка сетки на листе (75х120 мм):**")
    
    col_width, col_height = st.columns(2)
    
    with col_width:
        cols = st.number_input(
            "Штрихкодов по ШИРИНЕ (колонки):", 
            min_value=1, 
            max_value=10, 
            value=2, 
            step=1
        )
        
    with col_height:
        rows = st.number_input(
            "Штрихкодов по ВЫСОТЕ (строки):", 
            min_value=1, 
            max_value=15, 
            value=4, 
            step=1
        )
        
    items_per_page = cols * rows
    st.caption(f"Итого на одном листе получится: **{items_per_page} шт.**")

    draw_border = st.checkbox("Добавить чёрную рамочку вокруг каждого штрихкода", value=False)

if uploaded_file is not None:
    if st.button("Сформировать PDF", type="primary"):
        # Размеры холста в пунктах PDF (75x120 мм)
        page_w, page_h = 75 * 2.83465, 120 * 2.83465
        
        # Автоматический расчёт размера ячейки под выбранную сетку
        cell_w = page_w / cols
        cell_h = page_h / rows
        
        src_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        # Формируем список всех страниц с учётом повторов
        all_pages = []
        for page_num in range(len(src_doc)):
            for _ in range(int(copies)):
                all_pages.append(page_num)
                
        out_doc = fitz.open()
        total_items = len(all_pages)
        
        # Заполнение сетки
        for i in range(0, total_items, items_per_page):
            chunk = all_pages[i:i + items_per_page]
            out_page = out_doc.new_page(width=page_w, height=page_h)
            
            for idx, src_page_idx in enumerate(chunk):
                r = idx // cols
                c = idx % cols
                x0, y0 = c * cell_w, r * cell_h
                x1, y1 = x0 + cell_w, y0 + cell_h
                rect = fitz.Rect(x0, y0, x1, y1)
                
                # Вставляем штрихкод
                out_page.show_pdf_page(rect, src_doc, src_page_idx)
                
                # Рисуем рамку, если включена галочка
                if draw_border:
                    out_page.draw_rect(rect, color=(0, 0, 0), width=0.8)
                
        pdf_bytes = out_doc.tobytes()
        
        st.success("Готово!")
        st.download_button(
            label="Скачать готовый PDF (75х120 мм)",
            data=pdf_bytes,
            file_name="result_75x120.pdf",
            mime="application/pdf"
        )
