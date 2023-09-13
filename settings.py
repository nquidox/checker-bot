# general
DB = "checker.db"
DB_REQ_LIMIT = 150
checker_interval = 15

# tracker
LINK = "https://www.tokyotosho.info/rss.php"
FILTER = "1"
ENTRIES = ["150", "300", "450", "600", "750"]
RSS_LINK = f"{LINK}?filter={FILTER}&entries={ENTRIES[0]}"


if __name__ == "__main__":
    print("Not intended to run on its own.")
