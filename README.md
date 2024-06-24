# Custom scripts for my Badger 2040

- modified launcher
- refactored badge app

## References

- [Badger 2040 Firmware + Examples](https://github.com/pimoroni/badger2040): I basically copied these 
- [Getting Started with Badger 2040 & Badger 2040 W ](https://learn.pimoroni.com/article/getting-started-with-badger-2040)

### Badge
[apps/badge/badge.py](/apps/apps/badge/badge.py)

Customisable name badge example.

#### TODO:
- badge data files are json format, stored in `apps/badge/`
- images stored in /apps/badge

```json
{
  "topHeading": "company",
  "name": "name",
  "r1_title": "title 1",
  "r1_text": "text 1",
  "r1_title": "title 1",
  "r1_text": "text 1",
  "image": {
    "file": "badge.png", // png or jpg
    "width": 135,  // pixels
  }
}
```
