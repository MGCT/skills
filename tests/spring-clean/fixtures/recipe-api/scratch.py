# just me poking at the json encoder, ignore
import json
from datetime import datetime
print(json.dumps({"now": str(datetime.utcnow())}))
