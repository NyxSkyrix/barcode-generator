import fitz  # PyMuPDF
import streamlit as st
import datetime
import random
import string

st.set_page_config(page_title="Генератор этикеток", layout="centered")

st.title("Генератор сетки штрихкодов")
st.write("Автоматическая раскладка на этикетку 75х120 мм")

uploaded_file = st.file_uploader("Загрузите PDF файл", type=["pdf"])

# Настройки раскладки
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
    st.caption(f"Итого на одном листе помещается: **{items_per_page} шт.**")

    draw_border = st.checkbox("Добавить чёрную рамочку вокруг каждого штрихкода", value=False)

if uploaded_file is not None:
    # Размеры холста в pt (75x120 мм)
    page_w, page_h = 75 * 2.83465, 120 * 2.83465
    cell_w = page_w / cols
    cell_h = page_h / rows
    
    # Чтение исходного PDF
    uploaded_bytes = uploaded_file.read()
    src_doc = fitz.open(stream=uploaded_bytes, filetype="pdf")
    total_source_pages = len(src_doc)
    total_barcodes_to_print = total_source_pages * int(copies)
    
    # Предупреждение о пустых ячейках
    remainder = total_barcodes_to_print % items_per_page
    if remainder != 0:
        needed_copies = items_per_page // total_source_pages
        if needed_copies * total_source_pages < items_per_page:
            needed_copies += 1
            
        st.warning(
            f"⚠️ **Внимание:** На последней странице заполнено только **{remainder} из {items_per_page}** ячеек.\n\n"
            f"Чтобы полностью заполнить лист без пустых мест, увеличьте количество копий "
            f"до **{needed_copies}** (или до любого числа, кратного {items_per_page // total_source_pages or 1})."
        )

    # Собираем список всех штрихкодов с учетом повторов
    all_pages = []
    for page_num in range(total_source_pages):
        for _ in range(int(copies)):
            all_pages.append(page_num)
            
    out_doc = fitz.open()
    total_items = len(all_pages)
    
    # Заполнение всех страниц
    for i in range(0, total_items, items_per_page):
        chunk = all_pages[i:i + items_per_page]
        out_page = out_doc.new_page(width=page_w, height=page_h)
        
        for idx, src_page_idx in enumerate(chunk):
            r = idx // cols
            c = idx % cols
            x0, y0 = c * cell_w, r * cell_h
            x1, y1 = x0 + cell_w, y0 + cell_h
            rect = fitz.Rect(x0, y0, x1, y1)
            
            out_page.show_pdf_page(rect, src_doc, src_page_idx)
            
            if draw_border:
                out_page.draw_rect(rect, color=(0, 0, 0), width=0.8)

    # --- БЛОК ВИЗУАЛЬНОГО ПРЕДПРОСМОТРА ---
    st.write("---")
    st.subheader("Визуальный предпросмотр листа (75х120 мм)")
    
    # Рендерим 1-ю страницу итогового документа в картинку (150 DPI для четкости)
    preview_page = out_doc[0]
    pix = preview_page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    
    # Выводим картинку прямо по центру
    st.image(img_bytes, caption="Интерактивный макет первой страницы", width=280)
    
    # --- СКАЧИВАНИЕ ГОТОВОГО ФАЙЛА ---
    pdf_bytes = out_doc.tobytes()
    
    base_name = uploaded_file.name.rsplit('.', 1)[0]
    clean_name = "".join(c for c in base_name if c.isalnum() or c in ('_', '-')).rstrip()
    if not clean_name:
        clean_name = "labels"
        
    rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    output_filename = f"{clean_name}_{cols}x{rows}_x{copies}_{rand_id}.pdf"
    
    st.write("---")
    st.download_button(
        label=f"📥 Скачать готовый PDF ({output_filename})",
        data=pdf_bytes,
        file_name=output_filename,
        mime="application/pdf",
        type="primary"
    )
