# Local Piper voices

This demo uses the existing local Piper female voices from the Marykutty voice project.

Place these files on the Raspberry Pi:

- `models/piper/en/en_US-hfc_female-medium.onnx`
- `models/piper/en/en_US-hfc_female-medium.onnx.json`
- `models/piper/ml/ml_IN-meera-medium.onnx`
- `models/piper/ml/ml_IN-meera-medium.onnx.json`

Alternatively set:

- `PIPER_EN_MODEL=/full/path/to/en_US-hfc_female-medium.onnx`
- `PIPER_ML_MODEL=/full/path/to/ml_IN-meera-medium.onnx`

The `piper` executable must be available on PATH.
