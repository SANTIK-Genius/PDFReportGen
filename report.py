from utils import PDFReportGenerator
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Генератор PDF отчетов из CSV файлов")
    parser.add_argument("--input", "-i", default="data.csv", help="Входной CSV файл")
    parser.add_argument("--output", "-o", default="report.pdf", help="Выходной PDF файл")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Файл {args.input} не найден!")
        return

    print("🚀 Запуск генерации PDF отчёта...")
    generator = PDFReportGenerator()
    success = generator.generate_report(args.input, args.output)

    if success:
        print("🎉 Генерация завершена успешно!")
    else:
        print("💥 Произошла ошибка при генерации отчёта")

if __name__ == "__main__":
    main()