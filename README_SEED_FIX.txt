Rob's Code Wizard - Translation Map Seeder Fix
================================================

WHAT THIS DOES
--------------
Fixes the empty Translation tab issue by directly reading your canonical
VDT_CODES.xlsx and ODOT_CODES.xlsx and writing a populated
app/data/translation_map.json.

The seeder skips title rows automatically (scans first 10 rows looking
for the real header).

RUN ORDER
---------
1. Extract this zip into the Robs_Code_Wizard project root
   (where app\main.py lives).
2. Run seed_translation_map.bat
3. Restart Rob's Code Wizard.
4. Open the Translation tab - it should now show all entries.

XLSX LOCATIONS
--------------
The seeder looks for VDT_CODES.xlsx and ODOT_CODES.xlsx in:
  - app\data\
  - resources\
  - project root

Move or copy your catalog xlsx files to one of those if not already there.
