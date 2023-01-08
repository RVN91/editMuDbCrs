# editMuDbCrs

Opens a MIKE URBAN geodatabase and edits open channel cross sections

## How to run:

CMD-prompt for running the script:

```python
"pah for ArcMap python.exe" "path for CRSID.py"
"C:\Python27\ArcGIS10.3\python.exe" "C:\Users\Rasmus\Desktop\CRSID.py"
```

## PROBLEMS AND BUGS:

[u'110X175*1.1X1.75', u'110X160*1.1X1.6', u'110X160*1.1X1.6'] CRSID's do not have a a type ID. See code line below, where the they have been removed manually. Check if this causes any problems.

### For some reason 3 of the CRSID's do not have a type_id...

```python
crsid = crsid[:-3]
```

Reading coordinate table for CRSID "DAA_CRS_19" yields empty/non-existing values (empty list), so this CRSID is also skipped in the following line:

```python 
# If the coordinates of the CRSID is empty, skip it

if not tmp:
	print(crsd_unique[i])
	break
```
