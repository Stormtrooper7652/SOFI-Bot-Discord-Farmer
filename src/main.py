import random
import threading
import time
from config import DC_MAIN_TOKEN, DC_SECONDARY_TOKEN, DROP_LOG_FILE_PATH
from utils import webhook_log, ordermap
from discord_cmd import find_best_card, post_message, fetch_latest_drop, grab_card
from tqdm import tqdm
		
def run_task():
	iterations = 0
	while True:
		drop_account, secondary_account = (
			(DC_MAIN_TOKEN, DC_SECONDARY_TOKEN)
			if iterations % 2 == 0
			else (DC_SECONDARY_TOKEN, DC_MAIN_TOKEN)
		)

		webhook_log(f"Running drop, Interation [{iterations}]")
		code = post_message("sd", drop_account)
		if code >= 300: 
			webhook_log("Failed to send message", "Error")
			return
		time.sleep(5)

		webhook_log("Fetching drop data")
		drop, err = fetch_latest_drop(True)

		if not drop:
			webhook_log("Failed to fetch drop", "Warning")
			if err == "Delay":
				webhook_log("Timing error occurred, waiting 8 minutes", "Error")
				time.sleep(8 * 60)
			
			webhook_log("Refetching cards", "Warning")
			drop, err = fetch_latest_drop(False)
			if not drop:
				webhook_log("Fatel error fetch cards", "Error")
				raise Exception("Fatel error fetching cards")
		
		if drop_account == DC_MAIN_TOKEN:
			webhook_log("Updating drop log file")
			with open(DROP_LOG_FILE_PATH, "w") as f:
				f.write(str(int(time.time())))

		if drop:
			webhook_log("Successfully dropped", "Success")
			index_best, index_second = find_best_card(drop)
			
			webhook_log(f"Choosing cards [{index_best + 1}, {index_second + 1}]")
			index = index_best if drop_account == DC_MAIN_TOKEN else index_second
			code = grab_card(drop, index, drop_account)
			
			if code == None or code >= 300:
				webhook_log("Failed to grab card", "Error")
			else:
				state = "Success" if code < 300 else "Error"
				webhook_log(f"Grabbed {index+1}{ordermap[index+1]} card [{code}]", state)
		else:
			webhook_log("No drop found", "Error")
			return
		
		time.sleep(random.randint(7, 14))

		index = index_second if secondary_account == DC_SECONDARY_TOKEN else index_best
		code = grab_card(drop, index, secondary_account)

		if code == None or code >= 300:
			webhook_log("Failed to grab card", "Error")
		else:
			state = "Success" if code < 300 else "Error"
			webhook_log(f"Grabbed {index+1}{ordermap[index+1]} card [{code}]", state)

		delay = 5 + (8 - 5) * random.betavariate(2.0, 3.0)
		minutes = delay * 60
		webhook_log(f"Sleeping {round(delay, 1)} minutes")
		steps = round(minutes)
		sleep_time = minutes / steps
		for _ in tqdm(range(steps), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}s", desc=f"Sleeping", ncols=80):
			time.sleep(sleep_time)
		
		iterations += 1
		# TODO: Sleep schedule
		# TODO: Try to use discords on message api

if __name__ == "__main__":
	webhook_log("Checking last drop")
	last = 0
	try:
		with open(DROP_LOG_FILE_PATH) as f:
			try:
				last = int(f.read())
			except ValueError:
				webhook_log("Failed to parse drop log", "Error")
	except FileNotFoundError:
		webhook_log("No drop log found", "Warning")
	
	now = int(time.time())
	last += 8 * 60
	diff = last - now
	if diff > 0:
		webhook_log(f"Faulty drop timings, delaying execution ({diff})s", "Warning")
		time.sleep(diff)

	webhook_log("Initializing thread")	
	t1 = threading.Thread(target=run_task, daemon=True)
	t1.start()
	t1.join()