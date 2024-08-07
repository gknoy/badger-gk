# Custom scripts for my Badger 2040

- modified launcher
- refactored badge app

## References

- [Badger 2040 Firmware + Examples](https://github.com/pimoroni/badger2040): I basically copied these 
- [Getting Started with Badger 2040 & Badger 2040 W ](https://learn.pimoroni.com/article/getting-started-with-badger-2040)

### Badge app
[apps/badge/badge.py](/apps/apps/badge/badge.py): Customisable name badge program.
- BUTTON_UP and BUTTON_DOWN picks between badge configurations
- apps/badge/data/
  - JSON files define badge configs
  - image files referenced in configs are stored in /apps/badge/data/

```json
// example
{
    "heading": "Myriad Genetics",
    "name": "Gabriel Knoy",
    "r1_title": "gknoy@myriad.com",
    "r1_text": "",
    "r2_title": "Data Review Engineering",
    "r2_text": "",
    "image": {
        "file": "portrait-92x128-dithered.jpg",
        "width": 92,
        "dithered": true
    }
}
```
#### TODO:
- Fix responsiveness of picking differnt badges
- Allow arbitrary layout, especially of image
