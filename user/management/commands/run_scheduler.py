import schedule
import time
from user.validators.subscription_expired import is_subscription_active

schedule.every().day.at("12:00").do(is_subscription_active)

while True:
    schedule.run_pending()
    time.sleep(10)