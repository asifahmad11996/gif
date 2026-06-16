# FoxiGrow Bot Push Assets

Banner images and animated GIFs for @FoxiGrowbot task notifications.

## Structure

```
foxigrowbot/
├── banners/          # Static PNG banners (16:9, Telegram-friendly)
├── gifs/             # Animated GIF alerts
├── manifest/
│   └── push-assets.json   # Trigger → caption → asset mapping
└── scripts/
    └── generate_gifs.py   # Regenerate GIFs locally
```

## Banners

| File | Use case |
|------|----------|
| `task-center.png` | Daily digest, general task availability |
| `must-do-link-accounts.png` | Onboarding — link social accounts |
| `high-value-20-task.png` | $20 task spotlight (#11630) |
| `drip-tasks-soon.png` | Drip task teaser (3 releasing soon) |
| `daily-digest.png` | Top tasks roundup, idle user nudge |
| `download-register.png` | Download & Register task (#12209) |
| `project-activities-task-system.png` | Project activities overview (16:9) |
| `project-activities-task-system-vertical.png` | Same — vertical for Stories |
| `private-tasks-task-master.png` | Private tasks & Task Master (16:9) |
| `private-tasks-task-master-vertical.png` | Same — vertical for Stories |

## GIFs

| File | Use case |
|------|----------|
| `task-center-live.gif` | "21 tasks available" pulse animation |
| `must-do-link-accounts.gif` | Account linking reminder |
| `high-value-20-task.gif` | $20 task alert with coin rain |
| `drip-tasks-soon.gif` | Drip countdown animation |
| `new-task-alert.gif` | Generic new task / low-slots alert |
| `download-register.gif` | Download & Register task animation |
| `social-follow-earn.gif` | Rotating social follow highlights |

## Bot integration

Load `manifest/push-assets.json` and match on `trigger` (or `task_id` for task-specific pushes).

**Recommended send format (Telegram):**
1. Send GIF or banner photo first (GIF grabs attention in groups)
2. Follow with `caption` text from manifest
3. Attach inline `buttons` as URL keyboard

**Variables for templated captions:**
- `{task_name}`, `{task_id}`, `{fg_reward}`, `{usd_reward}`, `{slots}`

GIFs are generated from the matching banner artwork with Ken Burns zoom, glow pulse, and sparkle overlays (480×270, ~1.5MB each).

## Regenerate GIFs

```bash
cd foxigrowbot && python3 scripts/generate_gifs.py
```

Requires: `pip install pillow`
