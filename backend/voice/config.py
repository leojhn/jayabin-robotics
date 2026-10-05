# Local voice demo configuration. Cloud voice APIs are intentionally disabled.
PIPER_LANGUAGE_PRIORITY = ('en-IN', 'ml-IN')
PIPER_EN_MODEL = 'models/piper/en/en_US-hfc_female-medium.onnx'
PIPER_ML_MODEL = 'models/piper/ml/ml_IN-meera-medium.onnx'
HMS_API_BASE = "http://127.0.0.1:5000"
VOICE_API_TIMEOUT = 10
