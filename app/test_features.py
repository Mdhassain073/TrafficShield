# app/test_features.py — Test feature extraction

from app.parser import parse_log_file
from app.features import extract_features

LOG_FILE = "data/access.log"

records = parse_log_file(LOG_FILE)
features = extract_features(records)
print(features)
