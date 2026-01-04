"""Suno V5 music generation service.

使用 customMode=false，只提供提示词让 Suno 自由创作。
支持回调通知前端生成进度。
每次请求返回 2 首歌曲。
"""
import asyncio
import logging
from dataclasses import dataclass

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from moana.config import get_settings
from moana.services.music.base import BaseMusicService, MusicResult, MusicStyle
from moana.services.storage import get_storage_service

logger = logging.getLogger(__name__)


class SunoServiceError(Exception):
    """Base error for Suno service."""
    pass


class InsufficientBalanceError(SunoServiceError):
    """Raised when Suno account has insufficient credits."""
    pass


class ContentModerationError(SunoServiceError):
    """Raised when content is flagged by moderation."""
    pass


@dataclass
class TimestampedWord:
    """Single word with timestamp for karaoke-style display."""
    word: str
    start_s: float  # 开始时间（秒）
    end_s: float    # 结束时间（秒）
    success: bool   # 是否成功对齐


@dataclass
class SunoTrack:
    """Single track from Suno generation."""
    id: str
    audio_url: str
    stream_url: str
    cover_url: str
    video_url: str  # Suno 生成的视频 URL
    title: str
    tags: str
    duration: float
    prompt: str
    model: str
    lyric: str  # Suno 生成的实际歌词（纯文本）
    timestamped_lyrics: list[TimestampedWord] | None = None  # 带时间戳的歌词


@dataclass
class SunoGenerationResult:
    """Result containing both tracks from Suno."""
    task_id: str
    tracks: list[SunoTrack]
    status: str


class SunoMusicService(BaseMusicService):
    """Suno V5 music generation service.

    使用简单模式 (customMode=false)，只提供描述性提示词，
    让 Suno AI 自由发挥创作歌词和音乐。

    每次生成返回 2 首不同版本的歌曲。
    """

    # 回调状态常量
    CALLBACK_TEXT = "text"      # 歌词生成完成
    CALLBACK_FIRST = "first"    # 第一首歌完成
    CALLBACK_COMPLETE = "complete"  # 全部完成

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.suno_api_key
        self._api_base = settings.suno_api_base
        self._model = settings.suno_model
        # 回调 URL - 用于通知前端进度
        self._callback_base = getattr(settings, 'callback_base_url', 'https://example.com')

    @property
    def provider_name(self) -> str:
        return "suno"

    def build_music_prompt(
        self,
        theme_topic: str,
        theme_category: str,
        child_name: str,
        age_months: int,
        style: MusicStyle,
        favorite_characters: list[str] | None = None,
    ) -> str:
        """构建音乐生成提示词.

        注意：customMode=false 时，提示词最大 500 字符！
        使用中文提示词，精简但包含关键信息。
        """
        # 风格描述（中文）
        style_mapping = {
            MusicStyle.CHEERFUL: "欢快活泼",
            MusicStyle.GENTLE: "温柔舒缓",
            MusicStyle.PLAYFUL: "俏皮有趣",
            MusicStyle.LULLABY: "轻柔安眠",
            MusicStyle.EDUCATIONAL: "朗朗上口",
        }
        style_desc = style_mapping.get(style, "欢快活泼")

        # 年龄段
        if age_months < 24:
            age_desc = "1-2岁宝宝"
        elif age_months < 36:
            age_desc = "2-3岁幼儿"
        else:
            age_desc = "3-6岁儿童"

        # 主题类别
        category_desc = "习惯养成" if theme_category == "habit" else "认知启蒙"

        # 精简的中文提示词 (控制在 500 字符以内)
        prompt = f"""为{age_desc}创作一首关于「{theme_topic}」的中文儿歌。

风格：{style_desc}，旋律朗朗上口，副歌重复易记
主角：{child_name}（在歌词中自然融入名字）
类型：{category_desc}

要求：歌词简单、正向积极、适合幼儿"""

        # 如果有喜欢的角色，简短添加
        if favorite_characters and len(prompt) < 400:
            chars = "、".join(favorite_characters[:2])
            prompt += f"\n角色：{chars}"

        logger.debug(f"Music prompt length: {len(prompt)} chars")
        return prompt

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        prompt: str,
        style: MusicStyle = MusicStyle.CHEERFUL,
        callback_task_id: str | None = None,
    ) -> MusicResult:
        """Generate music using Suno V5 API.

        Args:
            prompt: 详细的音乐描述提示词
            style: 音乐风格（用于构建风格标签）
            callback_task_id: 可选的任务ID，用于回调通知

        Returns:
            MusicResult: 包含第一首歌曲的结果（两首都会保存）
        """
        # 1. 提交生成任务
        task_id = await self._create_task(prompt, callback_task_id)
        logger.info(f"Suno task created: {task_id}")

        # 2. 轮询等待完成 (最多 5 分钟)
        result = await self._poll_until_complete(task_id, timeout=300, interval=5)

        # 3. 下载并保存所有歌曲到本地存储，并获取时间戳歌词和音乐视频
        saved_tracks = []
        for i, track in enumerate(result.tracks):
            # 下载音频和封面
            local_url = await self._download_and_save(
                track.audio_url,
                f"suno_{task_id}_{i}"
            )
            local_cover = await self._download_and_save_image(
                track.cover_url,
                f"suno_cover_{task_id}_{i}"
            )

            # 获取时间戳歌词
            timestamped_lyrics = await self.get_timestamped_lyrics(task_id, track.id)
            timestamped_lyrics_data = [
                {
                    "word": w.word,
                    "start_s": w.start_s,
                    "end_s": w.end_s,
                }
                for w in timestamped_lyrics
            ]

            # 生成音乐视频（只为第一首歌生成，节省资源）
            local_video = ""
            if i == 0:
                local_video = await self.generate_and_wait_video(
                    task_id=task_id,
                    audio_id=track.id,
                    author="",
                    timeout=180,
                )

            # 如果本地封面下载失败，使用 Suno 原始封面 URL 作为备用
            final_cover = local_cover or track.cover_url

            saved_tracks.append({
                "id": track.id,
                "audio_url": local_url,
                "cover_url": final_cover,  # 优先本地，备用 Suno 原始 URL
                "suno_cover_url": track.cover_url,  # 始终保存 Suno 原始 URL
                "video_url": local_video,
                "title": track.title,
                "duration": track.duration,
                "tags": track.tags,
                "lyric": track.lyric,  # Suno 生成的实际歌词（纯文本）
                "timestamped_lyrics": timestamped_lyrics_data,  # 带时间戳的歌词
            })

        logger.info(f"Saved {len(saved_tracks)} tracks from Suno")

        # 返回第一首作为主结果，但保存所有歌曲信息
        primary = saved_tracks[0] if saved_tracks else {}
        primary_track = result.tracks[0] if result.tracks else None

        return MusicResult(
            audio_url=primary.get("audio_url", ""),
            duration=primary.get("duration", 0),
            lyrics=primary_track.lyric if primary_track else "",  # Suno 生成的实际歌词
            model=f"suno-{self._model.lower()}",
            style=style.value,
            format="mp3",
            # 额外信息：所有生成的歌曲
            extra={
                "task_id": task_id,
                "all_tracks": saved_tracks,  # 包含 audio_url, cover_url, suno_cover_url, video_url, timestamped_lyrics
                "primary_cover_url": primary.get("cover_url", ""),  # 优先本地，备用 Suno 原始
                "primary_suno_cover_url": primary.get("suno_cover_url", ""),  # Suno 原始封面 URL
                "primary_video_url": primary.get("video_url", ""),
                "primary_timestamped_lyrics": primary.get("timestamped_lyrics", []),
                "prompt": prompt,  # 保存原始提示词供参考
            },
        )

    async def generate_full(
        self,
        theme_topic: str,
        theme_category: str,
        child_name: str,
        age_months: int,
        style: MusicStyle = MusicStyle.CHEERFUL,
        favorite_characters: list[str] | None = None,
        callback_task_id: str | None = None,
    ) -> MusicResult:
        """完整的音乐生成流程，自动构建提示词.

        这是推荐的调用方式，会自动生成优化的提示词。
        """
        prompt = self.build_music_prompt(
            theme_topic=theme_topic,
            theme_category=theme_category,
            child_name=child_name,
            age_months=age_months,
            style=style,
            favorite_characters=favorite_characters,
        )

        return await self.generate(
            prompt=prompt,
            style=style,
            callback_task_id=callback_task_id,
        )

    async def _create_task(self, prompt: str, callback_task_id: str | None = None) -> str:
        """Submit music generation task to Suno API.

        使用 customMode=false，只提供 prompt，让 Suno 自由创作。
        """
        # 构建回调 URL
        callback_url = f"{self._callback_base}/api/v1/callback/suno"
        if callback_task_id:
            callback_url = f"{callback_url}?task_id={callback_task_id}"

        request_body = {
            "model": self._model,
            "customMode": False,  # 简单模式，只用提示词
            "instrumental": False,  # 有人声
            "prompt": prompt,
            "callBackUrl": callback_url,
        }

        logger.info(f"Creating Suno task with prompt: {prompt[:100]}...")
        logger.debug(f"Request body: {request_body}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._api_base}/api/v1/generate",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )

            if response.status_code == 429:
                raise InsufficientBalanceError("Suno account has insufficient credits")

            response.raise_for_status()
            result = response.json()

        if result.get("code") != 200:
            error_msg = result.get("msg", "Unknown error")
            logger.error(f"Suno API error: {error_msg}")
            raise SunoServiceError(f"Suno API error: {error_msg}")

        task_id = result.get("data", {}).get("taskId", "")
        if not task_id:
            raise SunoServiceError("No taskId in Suno response")

        return task_id

    async def _poll_until_complete(
        self, task_id: str, timeout: int = 300, interval: int = 5
    ) -> SunoGenerationResult:
        """Poll Suno API until task completes.

        Returns:
            SunoGenerationResult: 包含所有生成的歌曲
        """
        elapsed = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            while elapsed < timeout:
                response = await client.get(
                    f"{self._api_base}/api/v1/generate/record-info",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    params={"taskId": task_id},
                )
                response.raise_for_status()
                result = response.json()

                data = result.get("data", {})
                status = data.get("status", "")

                logger.info(f"Suno task {task_id} status: {status} (elapsed: {elapsed}s)")

                if status == "SUCCESS":
                    suno_data = data.get("response", {}).get("sunoData", [])
                    if not suno_data:
                        raise SunoServiceError("No audio data in SUCCESS response")

                    # 解析所有歌曲
                    tracks = []
                    for item in suno_data:
                        # Suno customMode=false 时，生成的歌词在 prompt 字段中
                        # customMode=true 时，歌词在 lyric/lyrics 字段
                        generated_lyric = (
                            item.get("lyric", "") or
                            item.get("lyrics", "") or
                            item.get("prompt", "")  # customMode=false 时歌词在 prompt 字段
                        )
                        # 视频 URL（Suno 会生成音乐视频）
                        video_url = (
                            item.get("videoUrl", "") or
                            item.get("video_url", "") or
                            item.get("sourceVideoUrl", "") or
                            item.get("source_video_url", "")
                        )
                        track = SunoTrack(
                            id=item.get("id", ""),
                            audio_url=item.get("audioUrl", "") or item.get("audio_url", ""),
                            stream_url=item.get("streamAudioUrl", "") or item.get("stream_audio_url", ""),
                            cover_url=item.get("imageUrl", "") or item.get("image_url", ""),
                            video_url=video_url,
                            title=item.get("title", ""),
                            tags=item.get("tags", ""),
                            duration=item.get("duration", 0),
                            prompt=item.get("prompt", ""),
                            model=item.get("modelName", "") or item.get("model_name", ""),
                            lyric=generated_lyric,
                        )
                        tracks.append(track)
                        logger.info(f"  Track: {track.title}, duration: {track.duration}s, lyric: {len(track.lyric)} chars, video: {bool(video_url)}")

                    return SunoGenerationResult(
                        task_id=task_id,
                        tracks=tracks,
                        status="SUCCESS",
                    )

                if status == "SENSITIVE_WORD_ERROR":
                    raise ContentModerationError("Content flagged by Suno moderation")

                if status in ("CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED", "CALLBACK_EXCEPTION"):
                    error_msg = data.get("errorMessage", "Unknown error")
                    raise SunoServiceError(f"Suno generation failed: {error_msg}")

                await asyncio.sleep(interval)
                elapsed += interval

        raise SunoServiceError(f"Suno task {task_id} timed out after {timeout}s")

    async def _download_and_save(self, remote_url: str, filename_prefix: str) -> str:
        """Download audio and save to local storage."""
        if not remote_url:
            return ""

        logger.info(f"Downloading audio: {remote_url[:50]}...")

        # 禁用代理，直连 Suno CDN
        async with httpx.AsyncClient(timeout=120.0, proxy=None) as client:
            response = await client.get(remote_url)
            response.raise_for_status()
            audio_data = response.content

        logger.info(f"Downloaded {len(audio_data)} bytes")

        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=audio_data,
            key=f"{filename_prefix}.mp3",
            content_type="audio/mpeg",
        )

        if not result.success:
            raise SunoServiceError(f"Failed to save audio: {result.error}")

        logger.info(f"Audio saved to: {result.url}")
        return result.url

    async def _download_and_save_image(self, remote_url: str, filename_prefix: str) -> str:
        """Download cover image and save to local storage.

        封面下载失败不应影响整体流程，返回空 URL 继续处理。
        """
        if not remote_url:
            return ""

        logger.info(f"Downloading cover: {remote_url[:50]}...")

        try:
            # 禁用代理，Suno CDN 通过代理访问会返回 403
            async with httpx.AsyncClient(timeout=60.0, proxy=None) as client:
                response = await client.get(remote_url)
                response.raise_for_status()
                image_data = response.content

            # 判断图片格式
            content_type = response.headers.get("content-type", "image/jpeg")
            ext = "jpg"
            if "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"

            storage = get_storage_service()
            result = await storage.upload_bytes(
                data=image_data,
                key=f"{filename_prefix}.{ext}",
                content_type=content_type,
            )

            if not result.success:
                logger.warning(f"Failed to save cover: {result.error}")
                return ""

            return result.url

        except httpx.HTTPStatusError as e:
            # CDN 返回 403/404 等错误，记录警告但不中断流程
            logger.warning(f"Cover download failed (HTTP {e.response.status_code}): {remote_url[:80]}")
            return ""
        except Exception as e:
            # 其他异常也不应中断主流程
            logger.warning(f"Cover download failed: {e}")
            return ""

    async def get_task_status(self, task_id: str) -> dict:
        """查询任务状态，供前端轮询使用."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self._api_base}/api/v1/generate/record-info",
                headers={"Authorization": f"Bearer {self._api_key}"},
                params={"taskId": task_id},
            )
            response.raise_for_status()
            result = response.json()

        data = result.get("data", {})
        return {
            "task_id": task_id,
            "status": data.get("status", "UNKNOWN"),
            "progress": self._estimate_progress(data.get("status", "")),
            "error_message": data.get("errorMessage"),
        }

    def _estimate_progress(self, status: str) -> int:
        """估算进度百分比."""
        progress_map = {
            "PENDING": 10,
            "TEXT_SUCCESS": 30,
            "FIRST_SUCCESS": 60,
            "SUCCESS": 100,
            "SENSITIVE_WORD_ERROR": 100,
            "CREATE_TASK_FAILED": 100,
            "GENERATE_AUDIO_FAILED": 100,
        }
        return progress_map.get(status, 20)

    async def get_timestamped_lyrics(
        self, task_id: str, audio_id: str
    ) -> list[TimestampedWord]:
        """获取带时间戳的歌词，用于卡拉OK式显示.

        Args:
            task_id: Suno 任务 ID
            audio_id: 音轨 ID

        Returns:
            带时间戳的歌词列表
        """
        logger.info(f"Fetching timestamped lyrics for task={task_id}, audio={audio_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._api_base}/api/v1/generate/get-timestamped-lyrics",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "taskId": task_id,
                    "audioId": audio_id,
                },
            )

            if response.status_code != 200:
                logger.warning(f"Failed to get timestamped lyrics: {response.status_code}")
                return []

            result = response.json()

        if result.get("code") != 200:
            logger.warning(f"Timestamped lyrics API error: {result.get('msg')}")
            return []

        aligned_words = result.get("data", {}).get("alignedWords", [])
        if not aligned_words:
            logger.warning("No aligned words in response")
            return []

        # 解析时间戳歌词
        timestamped = []
        for item in aligned_words:
            word = TimestampedWord(
                word=item.get("word", ""),
                start_s=item.get("startS", 0),
                end_s=item.get("endS", 0),
                success=item.get("success", False),
            )
            timestamped.append(word)

        logger.info(f"Got {len(timestamped)} timestamped words")
        return timestamped

    async def _download_and_save_video(self, remote_url: str, filename_prefix: str) -> str:
        """Download video and save to local storage."""
        if not remote_url:
            return ""

        logger.info(f"Downloading video: {remote_url[:50]}...")

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.get(remote_url)
            response.raise_for_status()
            video_data = response.content

        logger.info(f"Downloaded video: {len(video_data)} bytes")

        storage = get_storage_service()
        result = await storage.upload_bytes(
            data=video_data,
            key=f"{filename_prefix}.mp4",
            content_type="video/mp4",
        )

        if not result.success:
            logger.warning(f"Failed to save video: {result.error}")
            return ""

        return result.url

    async def create_music_video(
        self,
        task_id: str,
        audio_id: str,
        author: str = "",
        callback_task_id: str | None = None,
    ) -> str:
        """创建音乐视频（MP4 格式，带视觉效果）.

        Args:
            task_id: Suno 音乐生成任务 ID
            audio_id: 音轨 ID
            author: 视频中显示的作者名（可选，最多 50 字符）
            callback_task_id: 回调任务 ID

        Returns:
            视频任务 ID
        """
        callback_url = f"{self._callback_base}/api/v1/callback/suno/video"
        if callback_task_id:
            callback_url = f"{callback_url}?task_id={callback_task_id}"

        request_body = {
            "taskId": task_id,
            "audioId": audio_id,
            "callBackUrl": callback_url,
        }
        if author:
            request_body["author"] = author[:50]

        logger.info(f"Creating music video for task={task_id}, audio={audio_id}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._api_base}/api/v1/mp4/generate",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )

            if response.status_code != 200:
                logger.warning(f"Create video API returned {response.status_code}: {response.text[:200]}")
                return ""

            result = response.json()

        code = result.get("code")
        if code == 409:
            # 视频已存在，直接返回已有的任务ID
            video_task_id = result.get("data", {}).get("taskId", "")
            logger.info(f"Video already exists, task_id: {video_task_id}")
            return video_task_id

        if code != 200:
            logger.warning(f"Create video API error: {result.get('msg')}")
            return ""

        video_task_id = result.get("data", {}).get("taskId", "")
        logger.info(f"Video task created: {video_task_id}")
        return video_task_id

    async def get_music_video_info(self, video_task_id: str) -> dict:
        """获取音乐视频信息.

        Args:
            video_task_id: 视频任务 ID

        Returns:
            视频信息字典，包含 video_url, status 等
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self._api_base}/api/v1/mp4/record-info",
                headers={"Authorization": f"Bearer {self._api_key}"},
                params={"taskId": video_task_id},
            )

            if response.status_code != 200:
                logger.warning(f"Get video info API returned {response.status_code}")
                return {"status": "ERROR", "error": f"HTTP {response.status_code}"}

            result = response.json()

        if result.get("code") != 200:
            return {"status": "ERROR", "error": result.get("msg")}

        data = result.get("data", {})
        # Suno MP4 API 返回格式:
        # {
        #   "data": {
        #     "successFlag": "SUCCESS",
        #     "response": { "videoUrl": "..." }
        #   }
        # }
        success_flag = data.get("successFlag", "")
        video_response = data.get("response", {}) or {}
        video_url = video_response.get("videoUrl", "") or video_response.get("video_url", "")

        logger.info(f"Video info: successFlag={success_flag}, videoUrl={video_url[:50] if video_url else 'N/A'}")

        return {
            "status": success_flag or data.get("status", "UNKNOWN"),
            "video_url": video_url,
            "duration": data.get("duration", 0),
        }

    async def generate_and_wait_video(
        self,
        task_id: str,
        audio_id: str,
        author: str = "",
        timeout: int = 180,
        interval: int = 5,
    ) -> str:
        """创建音乐视频并等待完成，返回本地视频 URL.

        Args:
            task_id: Suno 音乐生成任务 ID
            audio_id: 音轨 ID
            author: 作者名
            timeout: 超时时间（秒）
            interval: 轮询间隔（秒）

        Returns:
            本地存储的视频 URL
        """
        video_task_id = await self.create_music_video(task_id, audio_id, author)
        if not video_task_id:
            return ""

        # 轮询等待视频完成
        elapsed = 0
        while elapsed < timeout:
            info = await self.get_music_video_info(video_task_id)
            status = info.get("status", "")
            logger.info(f"Video task {video_task_id} status: {status} (elapsed: {elapsed}s)")

            if status == "SUCCESS":
                video_url = info.get("video_url", "")
                if video_url:
                    # 下载并保存到本地
                    local_url = await self._download_and_save_video(
                        video_url,
                        f"suno_mv_{video_task_id}"
                    )
                    return local_url
                return ""

            if status in ("ERROR", "FAILED"):
                logger.warning(f"Video generation failed: {info}")
                return ""

            await asyncio.sleep(interval)
            elapsed += interval

        logger.warning(f"Video task {video_task_id} timed out after {timeout}s")
        return ""
