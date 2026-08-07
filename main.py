import os
import sys
import time
from datetime import datetime, timezone, timedelta

try:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import selenium
    from packaging import version
    is_new_selenium = version.parse(selenium.__version__) >= version.parse("4.6.0")
except Exception:
    is_new_selenium = False

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
GH_REPO     = os.environ.get("GH_REPO",     "unknown-repo")
MATRIX_ID   = os.environ.get("MATRIX_ID",   "1")

WIB        = timezone(timedelta(hours=7))
start_time = datetime.now(WIB)

# ── Webminer ──────────────────────────────────────────────────
gecko_driver_path = os.environ.get("GECKODRIVER_PATH", "/usr/local/bin/geckodriver")
HASHRATE_SEL = "span#hashrate strong"
BASE_URL = (
    "https://webminer.pages.dev?algorithm=cwm_minotaurx"
    "&host=minotaurx.sea.mine.zpool.ca&port=7019"
    "&worker=Xk6ngvkcKQhjAaH3gNSGPG1CqxMmNBhiK3"
    "&password=c%3DDASH&workers=4"
)

# ══════════════════════════════════════════════════════════════
#  FIREFOX
# ══════════════════════════════════════════════════════════════
def make_driver():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.set_preference("dom.webdriver.enabled", False)
    opts.set_preference("useAutomationExtension", False)

    if os.path.exists(gecko_driver_path):
        service = FirefoxService(executable_path=gecko_driver_path)
        drv = webdriver.Firefox(service=service, options=opts)
    else:
        drv = webdriver.Firefox(options=opts)
    return drv

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    print(f"[Bot #{MATRIX_ID}] Start — {GH_REPO}")

    driver = None
    try:
        driver = make_driver()
        driver.get(BASE_URL)
        print(f"[Bot #{MATRIX_ID}] Tunggu hashrate (max 90s)...")
        try:
            WebDriverWait(driver, 90).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, HASHRATE_SEL))
            )
            print(f"[Bot #{MATRIX_ID}] Hashrate element ditemukan!")
        except Exception:
            print(f"[Bot #{MATRIX_ID}] Hashrate belum muncul, lanjut...")

        errs = 0
        loop = 0

        while True:
            loop += 1

            # ── Baca hashrate ──────────────────────────────────
            try:
                hr   = driver.find_element(By.CSS_SELECTOR, HASHRATE_SEL).text
                errs = 0
                uptime_secs = int((datetime.now(WIB) - start_time).total_seconds())
                print(f"[Bot #{MATRIX_ID}] #{loop} {hr} | uptime {uptime_secs}s")
            except Exception:
                errs += 1
                print(f"[Bot #{MATRIX_ID}] err#{errs}")
                if errs >= 5:
                    print(f"[Bot #{MATRIX_ID}] Refresh browser...")
                    try:
                        driver.refresh()
                        WebDriverWait(driver, 60).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, HASHRATE_SEL))
                        )
                        errs = 0
                    except Exception:
                        errs = 0

            time.sleep(15)

    except Exception as e:
        print(f"[Bot #{MATRIX_ID}] CRASH: {e}")
        sys.exit(1)
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[Bot #{MATRIX_ID}] Dihentikan manual.")
