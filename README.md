# Light Off

A free **Douse Light** action for every party member. It removes the Light cantrip
(`LIGHT`) from the caster's equipped weapons, so a forgotten Light no longer gives away
a stealthy character. No Script Extender needed.

Published on Nexus Mods on 2026-11-15: https://www.nexusmods.com/baldursgate3/mods/26670
(v1.0.1, category Gameplay, tagged AI-Generated Content and AI Media).

Author: Sylvanas Cry (Nexus: SylvanasCry). Mod UUID: `20a56c3c-2d83-456c-a68d-0afd2eccb566`.
No dependencies.

Release files are in `nexus/`:
- `LightOff-<version>.zip` holds the pak and `info.json` for BG3 Mod Manager. It is built
  locally and not committed; download it from Nexus.
- `description.bbcode` and `summary.txt` are the texts for the Nexus page.
- `art/make_preview.py` builds the preview image for the Nexus page. It needs Pillow and
  the game's tooltip icon (`Game.pak`:
  `Public/Game/GUI/Assets/Tooltips/Icons/Spell_Evocation_Light.DDS`, converted to PNG).
  The icon is not committed.

The in-game mod manager shows thumbnails only for mods installed from mod.io. A
`Mods/<Folder>/mod_publish_logo.png` inside a sideloaded pak is ignored (tested on
2026-11-15: no thumbnail, endless spinner in the details panel), so the pak does not
ship one.

## How it works

- Vanilla Light on a creature lands on its main-hand weapon:
  `ApplyEquipmentStatus(MainHand,LIGHT,100,-1)` in `Target_Light`.
- `Shout_LightOff` hits all four weapon slots (melee and ranged, main hand and off hand)
  with `LIGHTOFF_REMOVER`, a zero-duration status whose `OnApplyFunctors` run
  `RemoveStatus(LIGHT)` on the item. It also removes `LIGHT` from the caster.
  This is the same pattern vanilla uses for its own item-light toggles
  (`MAG_MAGIC_ITEM_LIGHT_REMOVER`).
- The spell is greyed out unless the caster or one of their weapons carries `LIGHT`
  (`RequirementConditions`).
- It costs nothing and is not a spell (no components), so it works in combat and while
  silenced.
- Built-in item lights with their own toggle passive (`MAG_LIGHT_DIVINE`, for example
  Gontr Mael's "Glowing") are deliberately left alone. Removing their status directly
  would put the toggle out of sync.
- `LightOff_GrantSpell.txt` (Osiris) adds the shout to every member of `DB_Players` on
  each level load and to anyone who joins the party.

## Build

```
& "$env:APPDATA\Vortex\baldursgate3\mods\ExportTool-v1.20.4\tools\Divine.exe" `
    -g bg3 -a create-package -s "$PWD\src" -d "$PWD\LightOff.pak" -c lz4
```

Run this from this directory. Divine 1.20.4 requires absolute paths.

## Install

Copy `LightOff.pak` to `%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods\` and enable it
in the mod manager. Load order does not matter.

## Status

v1.0.0: verified in game on 2026-11-15 on an existing save (AMP + AMP Plus run).
- The shout appeared on the party after enabling the mod mid-save.
- It removed Light from an equipped staff.
- A hotbar position chosen by the player survives save and load. The goal only calls
  `AddSpell` when `HasSpell` is 0, so the spell is never re-added and re-placed.

v1.0.0 broke stealth: `SNEAKING` ends on `OnAttack`, which any cast raises, unless the
spell has `SpellFlags.Stealth` (vanilla `RemoveConditions`). v1.0.1 adds
`SpellFlags "IgnoreSilence;Stealth;Invisible"`, the same flags vanilla Jump uses. Verified
in game on 2026-11-15: after Light → Hide → Douse Light, the character stays in stealth.
