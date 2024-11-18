import os
import logging
from datetime import datetime
# from from_root import from_root

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

log_dir = 'ml_logs'

logs_path = os.path.join(log_dir, LOG_FILE)

os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=logs_path,format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",level=logging.DEBUG)