import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime

class PDFReportGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

        self.pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        self.pdf.add_font('DejaVu', 'I', 'DejaVuSansCondensed-Oblique.ttf', uni=True)

    def load_csv(self, file_path):
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except UnicodeDecodeError:

            try:
                df = pd.read_csv(file_path, encoding='cp1251')
                return df
            except:
                df = pd.read_csv(file_path, encoding='latin1')
                return df
        except Exception as e:
            raise Exception(f"Ошибка загрузки CSV файла: {e}")

    def create_title_page(self, title="Отчёт", subtitle="Генератор PDF отчётов"):
        self.pdf.add_page()

        self.pdf.set_font("DejaVu", "B", 24)
        self.pdf.set_text_color(41, 128, 185)

        self.pdf.cell(0, 60, title, ln=True, align="C")

        self.pdf.set_font("DejaVu", "I", 16)
        self.pdf.set_text_color(52, 152, 219)
        self.pdf.cell(0, 20, subtitle, ln=True, align="C")

        self.pdf.set_font("DejaVu", "", 12)
        self.pdf.set_text_color(100, 100, 100)
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.pdf.cell(0, 20, f"Сгенерировано: {current_date}", ln=True, align="C")

        self.pdf.ln(40)
        self.pdf.set_fill_color(41, 128, 185)
        self.pdf.cell(0, 2, "", ln=True, fill=True)

    def create_statistics_page(self, df):
        self.pdf.add_page()

        self.pdf.set_font("DejaVu", "B", 18)
        self.pdf.set_text_color(44, 62, 80)
        self.pdf.cell(0, 15, "Статистика данных", ln=True)
        self.pdf.ln(5)

        self.pdf.set_font("DejaVu", "B", 12)
        self.pdf.set_text_color(52, 73, 94)
        self.pdf.cell(0, 10, f"Общее количество записей: {len(df)}", ln=True)
        self.pdf.cell(0, 10, f"Количество столбцов: {len(df.columns)}", ln=True)
        self.pdf.ln(10)

        numeric_columns = df.select_dtypes(include=['number']).columns

        if len(numeric_columns) > 0:
            self.pdf.set_font("DejaVu", "B", 14)
            self.pdf.cell(0, 10, "Статистика числовых данных:", ln=True)
            self.pdf.ln(5)

            for col in numeric_columns:
                self.pdf.set_font("DejaVu", "B", 11)
                self.pdf.set_text_color(41, 128, 185)
                self.pdf.cell(0, 8, f"Столбец: {col}", ln=True)

                self.pdf.set_font("DejaVu", "", 10)
                self.pdf.set_text_color(0, 0, 0)
                stats_text = (
                    f"Среднее: {df[col].mean():.2f} | "
                    f"Медиана: {df[col].median():.2f} | "
                    f"Станд. отклонение: {df[col].std():.2f}"
                )
                self.pdf.cell(0, 6, stats_text, ln=True)
                self.pdf.ln(2)

        text_columns = df.select_dtypes(include=['object']).columns
        if len(text_columns) > 0:
            self.pdf.set_font("DejaVu", "B", 14)
            self.pdf.cell(0, 10, "Текстовые столбцы:", ln=True)
            self.pdf.ln(5)

            for col in text_columns:
                self.pdf.set_font("DejaVu", "B", 11)
                self.pdf.set_text_color(41, 128, 185)
                self.pdf.cell(0, 8, f"Столбец: {col}", ln=True)

                self.pdf.set_font("DejaVu", "", 10)
                self.pdf.set_text_color(0, 0, 0)
                unique_count = df[col].nunique()
                self.pdf.cell(0, 6, f"Уникальных значений: {unique_count}", ln=True)
                self.pdf.ln(2)

    def create_table_page(self, df, max_rows_per_page=25):
        rows_per_page = max_rows_per_page
        total_rows = len(df)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

        for page_num in range(total_pages):
            self.pdf.add_page()

            self.pdf.set_font("DejaVu", "B", 16)
            self.pdf.set_text_color(44, 62, 80)
            self.pdf.cell(0, 15, f"Таблица данных (страница {page_num + 1}/{total_pages})", ln=True)
            self.pdf.ln(5)

            self._draw_table_header(df.columns.tolist())

            start_idx = page_num * rows_per_page
            end_idx = min((page_num + 1) * rows_per_page, total_rows)

            for i in range(start_idx, end_idx):
                self._draw_table_row(df.iloc[i].tolist(), i)

    def _draw_table_header(self, headers):
        self.pdf.set_fill_color(52, 152, 219)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("DejaVu", "B", 10)

        col_width = 190 / len(headers)

        for header in headers:

            display_header = str(header)[:15] + "..." if len(str(header)) > 15 else str(header)
            self.pdf.cell(col_width, 10, display_header, border=1, align="C", fill=True)

        self.pdf.ln()

    def _draw_table_row(self, row, row_index):
        """Отрисовка строки таблицы"""
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("DejaVu", "", 8)

        if row_index % 2 == 0:
            self.pdf.set_fill_color(245, 245, 245)
        else:
            self.pdf.set_fill_color(255, 255, 255)

        col_width = 190 / len(row)

        for cell in row:

            cell_str = str(cell)
            display_cell = cell_str[:15] + "..." if len(cell_str) > 15 else cell_str
            self.pdf.cell(col_width, 8, display_cell, border=1, align="C", fill=True)

        self.pdf.ln()

    def generate_report(self, csv_file_path, output_file="report.pdf"):
        try:

            df = self.load_csv(csv_file_path)

            self.create_title_page("Аналитический отчёт", f"На основе файла: {os.path.basename(csv_file_path)}")
            self.create_statistics_page(df)
            self.create_table_page(df)

            self.pdf.output(output_file)
            print(f"✅ Отчёт успешно сгенерирован: {output_file}")
            print(f"📊 Обработано записей: {len(df)}")
            print(f"📋 Количество столбцов: {len(df.columns)}")

            return True

        except Exception as e:
            print(f"❌ Ошибка при генерации отчёта: {e}")
            return False