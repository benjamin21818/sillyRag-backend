import os
import numpy as np
import sherpa_onnx
from .asr_interface import ASRInterface
from .utils import download_and_extract, check_and_extract_local_file
import onnxruntime
from src.utils.logger import get_logger
logger = get_logger(__name__)


class VoiceRecognition(ASRInterface):
    """
    语音识别类，基于 sherpa-onnx 实现。
    支持多种模型类型，如 paraformer, transducer, whisper, sense_voice 等。
    """
    def __init__(
        self,
        model_type: str = "paraformer",  # 模型类型，默认为 paraformer。可选值: "transducer", "nemo_ctc", "wenet_ctc", "whisper", "tdnn_ctc", "sense_voice", "fire_red_asr"
        encoder: str = None,  # Transducer 模型的编码器路径
        decoder: str = None,  # Transducer 模型的解码器路径
        joiner: str = None,  # Transducer 模型的连接器路径
        paraformer: str = None,  # Paraformer 模型的 onnx 文件路径
        nemo_ctc: str = None,  # NeMo CTC 模型的 onnx 文件路径
        wenet_ctc: str = None,  # WeNet CTC 模型的 onnx 文件路径
        tdnn_model: str = None,  # TDNN 模型的 onnx 文件路径
        whisper_encoder: str = None,  # Whisper 模型的编码器路径
        whisper_decoder: str = None,  # Whisper 模型的解码器路径
        sense_voice: str = None,  # SenseVoice 模型的 onnx 文件路径
        fire_red_asr_encoder: str = None,  # FireRedASR 模型的编码器路径
        fire_red_asr_decoder: str = None,  # FireRedASR 模型的解码器路径
        tokens: str = None,  # 词表文件路径 (tokens.txt)
        hotwords_file: str = "",  # 热词文件路径
        hotwords_score: float = 1.5,  # 热词得分
        modeling_unit: str = "",  # 热词的建模单元
        bpe_vocab: str = "",  # BPE 词表路径，用于热词
        num_threads: int = 1,  # 神经网络计算使用的线程数
        whisper_language: str = "",  # Whisper 模型的目标语言
        whisper_task: str = "transcribe",  # Whisper 模型的任务类型 (transcribe 或 translate)
        whisper_tail_paddings: int = -1,  # Whisper 模型的尾部填充帧数
        blank_penalty: float = 0.0,  # 空白符号的惩罚值
        decoding_method: str = "greedy_search",  # 解码方法 (greedy_search 或 modified_beam_search)
        debug: bool = False,  # 是否显示调试信息
        sample_rate: int = 16000,  # 采样率，默认 16000Hz
        feature_dim: int = 80,  # 特征维度，默认 80
        use_itn: bool = True,  # 是否对 SenseVoice 模型使用逆文本规范化 (ITN)
        provider: str = "cpu",  # 推理设备 (cpu 或 cuda)
    ) -> None:
        self.model_type = model_type
        self.encoder = encoder
        self.decoder = decoder
        self.joiner = joiner
        self.paraformer = paraformer
        self.nemo_ctc = nemo_ctc
        self.wenet_ctc = wenet_ctc
        self.tdnn_model = tdnn_model
        self.whisper_encoder = whisper_encoder
        self.whisper_decoder = whisper_decoder
        self.sense_voice: str = sense_voice
        self.fire_red_asr_encoder = fire_red_asr_encoder
        self.fire_red_asr_decoder = fire_red_asr_decoder
        self.tokens = tokens
        self.hotwords_file = hotwords_file
        self.hotwords_score = hotwords_score
        self.modeling_unit = modeling_unit
        self.bpe_vocab = bpe_vocab
        self.num_threads = num_threads
        self.whisper_language = whisper_language
        self.whisper_task = whisper_task
        self.whisper_tail_paddings = whisper_tail_paddings
        self.blank_penalty = blank_penalty
        self.decoding_method = decoding_method
        self.debug = debug
        self.SAMPLE_RATE = sample_rate
        self.feature_dim = feature_dim
        self.use_itn = use_itn

        # 检查是否有可用的 CUDA 提供程序，以便使用 GPU 加速
        self.provider = provider
        if self.provider == "cuda":
            try:
                if "CUDAExecutionProvider" not in onnxruntime.get_available_providers():
                    logger.warning(
                        "CUDA provider not available for ONNX. Falling back to CPU."
                    )
                    self.provider = "cpu"
            except ImportError:
                logger.warning("ONNX Runtime not installed. Falling back to CPU.")
                self.provider = "cpu"
        logger.info(f"Sherpa-Onnx-ASR: Using {self.provider} for inference")

        # 创建识别器实例
        self.recognizer = self._create_recognizer()

    def _create_recognizer(self):
        """
        根据 model_type 创建对应的 OfflineRecognizer 实例
        """
        if self.model_type == "transducer":
            recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
                encoder=self.encoder,
                decoder=self.decoder,
                joiner=self.joiner,
                tokens=self.tokens,
                num_threads=self.num_threads,
                sample_rate=self.SAMPLE_RATE,
                feature_dim=self.feature_dim,
                decoding_method=self.decoding_method,
                hotwords_file=self.hotwords_file,
                hotwords_score=self.hotwords_score,
                modeling_unit=self.modeling_unit,
                bpe_vocab=self.bpe_vocab,
                blank_penalty=self.blank_penalty,
                debug=self.debug,
                provider=self.provider,
            )
        elif self.model_type == "paraformer":
            recognizer = sherpa_onnx.OfflineRecognizer.from_paraformer(
                paraformer=self.paraformer,
                tokens=self.tokens,
                num_threads=self.num_threads,
                sample_rate=self.SAMPLE_RATE,
                feature_dim=self.feature_dim,
                decoding_method=self.decoding_method,
                debug=self.debug,
                provider=self.provider,
            )
        elif self.model_type == "nemo_ctc":
            recognizer = sherpa_onnx.OfflineRecognizer.from_nemo_ctc(
                model=self.nemo_ctc,
                tokens=self.tokens,
                num_threads=self.num_threads,
                sample_rate=self.SAMPLE_RATE,
                feature_dim=self.feature_dim,
                decoding_method=self.decoding_method,
                debug=self.debug,
                provider=self.provider,
            )
        elif self.model_type == "wenet_ctc":
            recognizer = sherpa_onnx.OfflineRecognizer.from_wenet_ctc(
                model=self.wenet_ctc,
                tokens=self.tokens,
                num_threads=self.num_threads,
                sample_rate=self.SAMPLE_RATE,
                feature_dim=self.feature_dim,
                decoding_method=self.decoding_method,
                debug=self.debug,
                provider=self.provider,
            )
        elif self.model_type == "whisper":
            recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
                encoder=self.whisper_encoder,
                decoder=self.whisper_decoder,
                tokens=self.tokens,
                num_threads=self.num_threads,
                decoding_method=self.decoding_method,
                debug=self.debug,
                language=self.whisper_language,
                task=self.whisper_task,
                tail_paddings=self.whisper_tail_paddings,
                provider=self.provider,
            )
        elif self.model_type == "tdnn_ctc":
            recognizer = sherpa_onnx.OfflineRecognizer.from_tdnn_ctc(
                model=self.tdnn_model,
                tokens=self.tokens,
                sample_rate=self.SAMPLE_RATE,
                feature_dim=self.feature_dim,
                num_threads=self.num_threads,
                decoding_method=self.decoding_method,
                debug=self.debug,
                provider=self.provider,
            )
        elif self.model_type == "sense_voice":
            if not self.sense_voice or not os.path.isfile(self.sense_voice):
                if self.sense_voice.startswith(
                    "./models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17"
                ):
                    logger.warning(
                        "SenseVoice model not found. Downloading the model..."
                    )

                    url = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2"
                    output_dir = "./models"
                    # check the local file first before download
                    local_result = check_and_extract_local_file(url, output_dir)

                    if local_result is None:
                        logger.info("Local file not found. Downloading...")
                        download_and_extract(url, output_dir)
                    else:
                        logger.info("Local file found. Using existing file.")
                    # download_and_extract(
                    #     url="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2",
                    #     output_dir="./models",
                    # )
                else:
                    logger.critical(
                        "The SenseVoice model is missing. Please provide the path to the model.onnx file."
                    )
            recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=self.sense_voice,
                tokens=self.tokens,
                num_threads=self.num_threads,
                use_itn=self.use_itn,
                debug=self.debug,
                provider=self.provider,
            )
        elif self.model_type == "fire_red_asr":
            recognizer = sherpa_onnx.OfflineRecognizer.from_fire_red_asr(
                encoder=self.fire_red_asr_encoder,
                decoder=self.fire_red_asr_decoder,
                tokens=self.tokens,
                num_threads=self.num_threads,
                decoding_method=self.decoding_method,
                debug=self.debug,
                provider=self.provider,
            )
        else:
            raise ValueError(f"Invalid model type: {self.model_type}")

        return recognizer

    def transcribe_np(self, audio: np.ndarray) -> str:
        """
        使用 numpy 数组格式的音频数据进行转写。

        Args:
            audio (np.ndarray): 音频数据，通常为 float32 类型，采样率应与模型要求一致（如 16000Hz）。

        Returns:
            str: 识别出的文本。
        """
        stream = self.recognizer.create_stream()
        stream.accept_waveform(self.SAMPLE_RATE, audio)
        self.recognizer.decode_streams([stream])
        return stream.result.text
