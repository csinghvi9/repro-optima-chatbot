from enum import Enum


class VideoCategory(str, Enum):
    UNDERSTANDINGIVF = "understanding-ivf"
    DOCTOR = "final-doctor-videos"
    PATIENT = "final-patient-videos"
    IVFCOST = "ivf-cost"
    SUCCESSRATE = "success-rate"


class Languages(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    MARATHI = "marathi"
    GUJARATI = "gujarati"
    BENGALI = "bengali"
    PUNJABI = "punjabi"
    KANADA = "kanada"
    TAMIL = "tamil"
    TELUGU = "telugu"
    ASSAMESE = "assamese"
    ODIA = "odia"
