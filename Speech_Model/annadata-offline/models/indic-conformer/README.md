---
license: mit
pipeline_tag: automatic-speech-recognition
---
# **IndicConformer**
AI4Bharat's IndicConformers is a suite of ASR models built to deliver accurate speech-to-text conversion in all 22 official Indian languages. By leveraging cutting-edge deep learning techniques, these models provide precise transcriptions. As the country's first open-source ASR system covering such a vast array of languages, AI4Bharat Indic Conformer is a transformative tool for making technology more inclusive and accessible to all. IndicConformer is released under the MIT license.

## **Model Details**
- **Model Name:** IndicConformer-600M-Multi
- **Repository:** [ai4bharat/indic-conformer-600m-multilingual](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- **Architecture:** Multilingual Conformer-based Hybrid CTC + RNNT ASR model
- **Parameter Size:** 600M
- **Languages Supported:** IN-22

---

## **Model Usage**
This model can be used to transcribe speech in various Indian languages. It supports two decoding strategies:  
- **CTC (Connectionist Temporal Classification)**
- **RNNT (Recurrent Neural Network Transducer)**

### **Installation**
Ensure that you have `transformers` and `torchaudio` installed:
```bash
pip install transformers torchaudio "onnxruntime==1.20.1" "onnx==1.20.1" "onnxruntime-gpu==1.20.1"
```

### **Inference Example**
```python
from transformers import AutoModel
import torch, torchaudio

# Load the model
model = AutoModel.from_pretrained("ai4bharat/indic-conformer-600m-multilingual", trust_remote_code=True)

# Load an audio file
wav, sr = torchaudio.load("audio.flac")
wav = torch.mean(wav, dim=0, keepdim=True)

target_sample_rate = 16000  # Expected sample rate
if sr != target_sample_rate:
    resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sample_rate)
    wav = resampler(wav)

# Perform ASR with CTC decoding
transcription_ctc = model(wav, "hi", "ctc")
print("CTC Transcription:", transcription_ctc)

# Perform ASR with RNNT decoding
transcription_rnnt = model(wav, "hi", "rnnt")
print("RNNT Transcription:", transcription_rnnt)
```

## **Supported Languages**
IndicConformer-600M-Multi is trained for **22 officially recognized languages of India**, including:
- Assamese(`as`)
- Bengali(`bn`)
- Bodo(`brx`)
- Dogri(`doi`)
- Gujarati(`gu`)
- Hindi(`hi`)
- Kannada(`kn`)
- Konkani(`kok`)
- Kashmiri(`ks`)
- Maithili(`mai`)
- Malayalam(`ml`)
- Manipuri(`mni`)
- Marathi(`mr`)
- Nepali(`ne`)
- Odia(`or`)
- Punjabi(`pa`)
- Sanskrit(`sa`)
- Santali(`sat`)
- Sindhi(`sd`)
- Tamil(`ta`)
- Telugu(`te`)
- Urdu(`ur`)

The tokenizers used for these languages can be found [here](https://github.com/AI4Bharat/IndicVoices/tree/master/artifacts/tokenizers)

## **Contact**
For any questions or feedback, please contact:

- Tahir Javed (tahir@cse.iitm.ac.in)
- Kaushal Bhogale (CS22D006@cse.iitm.ac.in)