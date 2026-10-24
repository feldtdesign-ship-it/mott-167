# 167 Mott Street, one door of two

One storefront on the west side of Mott between Broome and Grand, Manhattan. Two shopfronts under a seven-storey walk-up: one is a candle studio open till ten, the other went dark in the last 5 to 14 months and is listed with Meridian Retail Leasing at $6,750 a month, reduced from $7,000, after first appearing with KSR at rent on request. Public data, gathered 1 October 2026; listing updated October 2026.

**Live page:** https://feldtdesign-ship-it.github.io/mott-167/

- `index.html` – one page. Part one: scroll-driven camera through the block model, the lot, how long dark, tenants and owners, the trains, the block, the rent. Part two: the numbers.
- `live-wall.html` – the six nearest NYC DOT cameras. The closest is 197 m away. None sees Mott Street.
- `og.jpg` – the link-preview card, 1200 × 630, made by the build.
- `data/` – the pulls. `data/tenants.json` is the tenant and ownership timeline with a source for every line and a list of what is not established. `data/raw/` is the building's own record: PLUTO, storefront registry, ACRIS, DOB, ECB, HPD, 311, crashes, curbs.
- `frames/` – Blender renders of the block and camera frames from 1 October 2026.
- `assets/` – the Draco-compressed block model, 549 KB, including a detailed 167 Mott.
- `build/` – in the order they run:
  1. `pull_raw.py` – the building's record
  2. `pull.py` – transit, cameras, map layers, weather
  3. `build_mott.py` – the Blender block model and the building (`mott_167.blend`)
  4. `make_template.py` – assembles `mott_template.html` from `mott_head.html`, `mott_body.html` and the Clinton page's styles and chart code
  5. `build_page.py` – data into `index.html`
  6. `build_wall.py` – `live-wall.html`
  7. `make_card.sh` – `og.jpg`

## How long dark

The DOF storefront registry has filings for this lot for 2019–20 and 2020–21 only, both shops "not vacant", so the owner's word does not date it. The bracket comes from two archived pages: the last tenant's own site still gave 167 Mott on 17 July 2025, and the broker's listing was live with immediate possession on 17 April 2026. That the listed space is that tenant's shopfront is an inference. Confirm at the door.

## What is not real yet

The shopfronts, windows and fire escape on the 167 Mott model are drawn from the lot record and the listing (25.3 ft front, two commercial units, 10 ft of frontage each), not from a photograph. The body is the city's own outline at the recorded roof height. A sidewalk shed (permit of 2 July 2024) is in the Blender file, hidden.

## Where the numbers come from

- MTA subway hourly ridership, data.ny.gov, complexes 103 (Bowery), 409 (Spring St), 231 (Grand St), 623 (Canal St)
- MTA bus stop-level hourly ridership, eight stops inside 300 m (M1, M103)
- NYC DOT Automated Traffic Volume Counts: nothing on Mott; Elizabeth St, Grand to Broome, November 2013
- DOF Storefront Registry, BBL 1004710046 and every filing within 250 m
- NYC Motor Vehicle Collisions, Planimetric Database, building footprints, street centerline, 2015 street tree census, PLUTO, ACRIS, DOB, ECB, 311
- NYC DOT camera network, Open-Meteo daily archive, Citi Bike GBFS
- KSR listing (archived 17 April 2026), Meridian Retail Leasing flyer (October 2026), LoopNet 39571143, the tenants' own pages

Nobody counts the people passing this door. The page says so where it matters.
