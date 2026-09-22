import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Генератор этикеток", layout="centered")

st.title("Генератор сетки штрихкодов")
st.write("Автоматическая раскладка на этикетку 75х120 мм")

uploaded_file = st.file_uploader("Загрузите PDF файл", type=["pdf"])

# Контейнер с настройками сетки и оформления
with st.container():
    st.subheader("Настройки раскладки")
    
    col1, col2 = st.columns(2)
    
    with col1:
        copies = st.number_input(
            "Сколько копий каждого штрихкода сделать?", 
            min_value=1, 
            value=1, 
            step=1
        )
        
    with col2:
        grid_option = st.selectbox(
            "Количество штрихкодов на 1 листе:",
            options=["8 штук (2x4)", "10 штук (2x5)"]
        )

    draw_border = st.checkbox("Добавить чёрную рамочку вокруг каждого штрихкода", value=False)

if uploaded_file is not None:
    if st.button("Сформировать PDF", type="primary"):
        # Размеры в pt (75x120 мм)
        page_w, page_h = 75 * 2.83465, 120 * 2.83465
        
        # Определяем параметры сетки в зависимости от выбора
        if "10" in grid_option:
            cols, rows = 2, 5
            items_per_page = 10
        else:
            cols, rows = 2, 4
            items_per_page = 8
            
        cell_w, cell_h = page_w / cols, page_h / rows
        
        src_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        # Формируем список всех страниц с учётом повторов
        all_pages = []
        for page_num in range(len(src_doc)):
            for _ in range(int(copies)):
                all_pages.append(page_num)
                
        out_doc = fitz.open()
        total_items = len(all_pages)
        
        # Нарезаем по ячейкам на холст 75х120 мм
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
                
                # Если включена галочка — рисуем чёрную рамку вокруг ячейки
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
