from database import init_db
from crawler import crawl_dataset
from report_generator import generate_report

def main():
    init_db()
    crawl_dataset()
    generate_report()
    print("\n🎯 DONE! Open: output/report.html in browser")

if __name__ == "__main__":
    main()
