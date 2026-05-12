# reAPI Model Examples

This file is a bundled quick reference, not the canonical source. For current
model-specific parameters and pricing, use `https://reapi.ai/docs`.

The CLI reads `references/models.json` for `models` and `example` commands.

## Image Models

### `gpt-image-2`

Endpoint: `images`

```json
{
  "model": "gpt-image-2",
  "prompt": "a cute red panda eating bamboo, photorealistic",
  "size": "1:1"
}
```

Common fields: `model`, `prompt`, `size`, `resolution`, `n`, `image_urls`.

### `gpt-image-2-official`

Endpoint: `images`

```json
{
  "model": "gpt-image-2-official",
  "prompt": "a studio product photo of a ceramic espresso cup",
  "size": "1:1",
  "quality": "medium"
}
```

Common fields: `model`, `prompt`, `size`, `quality`, `n`, `image_urls`,
`mask_url`, `background`, `output_format`, `output_compression`.

### Gemini image preview family

Endpoint: `images`

Model IDs include:

- `gemini-2.5-flash-image-preview`
- `gemini-2.5-flash-image-preview-official`
- `gemini-3-pro-image-preview`
- `gemini-3-pro-image-preview-official`
- `gemini-3.1-flash-image-preview`
- `gemini-3.1-flash-image-preview-official`

Example:

```json
{
  "model": "gemini-3-pro-image-preview",
  "prompt": "editorial fashion portrait, clean studio lighting",
  "size": "1:1",
  "n": 1
}
```

Common fields: `model`, `prompt`, `size`, `resolution`, `n`, `image_urls`.
For Google search grounding fields such as `google_search` and
`google_image_search`, check
`https://reapi.ai/docs/gemini-3-1-flash-image-preview`.

### `doubao-seedream-5-0-lite`

Endpoint: `images`

```json
{
  "model": "doubao-seedream-5-0-lite",
  "prompt": "a bright illustrated travel poster for Kyoto",
  "aspect_ratio": "3:4",
  "resolution": "2K",
  "n": 1
}
```

Common fields: `model`, `prompt`, `aspect_ratio`, `resolution`, `n`,
`image_urls`, `sequential_image_generation`,
`sequential_image_generation_options`.

## Video Models

### Seedance 2.0 family

Endpoint: `videos`

Model IDs include:

- `doubao-seedance-2.0`
- `doubao-seedance-2.0-fast`
- `doubao-seedance-2.0-face`
- `doubao-seedance-2.0-fast-face`

```json
{
  "model": "doubao-seedance-2.0",
  "prompt": "a cinematic red panda walking through bamboo",
  "duration": 5,
  "resolution": "720p",
  "size": "16:9"
}
```

Common fields: `model`, `prompt`, `duration`, `size`, `resolution`, `seed`,
`generate_audio`, `return_last_frame`, `image_urls`, `image_with_roles`,
`video_urls`, `audio_urls`, `tools`.

### Seedance 2.0 beta family

Endpoint: `videos`

Model IDs include:

- `seedance-2.0-beta`
- `seedance-2.0-fast-beta`

```json
{
  "model": "seedance-2.0-beta",
  "prompt": "a handheld shot of a robot barista making latte art",
  "duration": 5,
  "aspect_ratio": "16:9",
  "resolution": "720p"
}
```

Common fields: `model`, `prompt`, `duration`, `aspect_ratio`, `resolution`,
`generate_audio`, `return_last_frame`, `first_frame_url`, `last_frame_url`,
`reference_image_urls`, `reference_video_urls`, `reference_audio_urls`,
`web_search`, `nsfw_checker`.

### `happyhorse-1.0` and `happyhorse-1.0-official`

Endpoint: `videos`

```json
{
  "model": "happyhorse-1.0",
  "prompt": "a playful clay animation of a tiny chef cooking pancakes",
  "duration": 5,
  "resolution": "720p",
  "size": "16:9"
}
```

Common fields: `model`, `prompt`, `duration`, `resolution`, `size`,
`first_frame_image`, `image_urls`, `video_url`, `audio_setting`, `watermark`.

### `enhance-video-1.0`

Endpoint: `videos`

```json
{
  "model": "enhance-video-1.0",
  "video_url": "https://example.com/input.mp4",
  "resolution": "1080p",
  "tool_version": "standard"
}
```

Common fields: `model`, `video_url`, `resolution`, `tool_version`, `scene`,
`resolution_limit`, `fps`, `client_token`, `callback_args`.

### Vidu Q3

Endpoint: `videos`

Model IDs include:

- `viduq3-pro`
- `viduq3-turbo`

```json
{
  "model": "viduq3-pro",
  "prompt": "a sweeping drone shot over a neon coastal city",
  "duration": 5,
  "size": "16:9"
}
```

Common fields: `model`, `prompt`, `duration`, `size`, `image_urls`,
`first_frame_image`, `last_frame_image`, `audio`.

### `grok-imagine-1.0-video`

Endpoint: `videos`

```json
{
  "model": "grok-imagine-1.0-video",
  "prompt": "a surreal glass forest under moonlight",
  "duration": 6,
  "aspect_ratio": "16:9"
}
```

Common fields: `model`, `prompt`, `duration`, `aspect_ratio`, `image_urls`.

### VEO 3.1 family

Endpoint: `videos`

Model IDs include:

- `veo3.1-fast`
- `veo3.1-quality`
- `veo3.1-lite`
- `veo3.1-fast-official`
- `veo3.1-quality-official`

```json
{
  "model": "veo3.1-fast",
  "prompt": "a documentary shot of waves crashing against black rocks",
  "aspect_ratio": "16:9"
}
```

Common fields vary by channel. Check `https://reapi.ai/docs/veo3-1` before
using advanced fields such as `first_frame_image`, `last_frame_image`,
`negative_prompt`, `seed`, `sample_count`, `generate_audio`,
`person_generation`, `resize_mode`, `enhance_prompt`, `enable_gif`,
`generation_type`, `source_task_id`, and `raw`.
