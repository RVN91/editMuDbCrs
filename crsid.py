# File name:    CRSD.py
# Author:       Rasmus Nielsen
# Date created: 06/06/2017
# 
# Edits MIKE URBAN open channel cross sections

# -*- coding: utf-8 -*-  
# Load MIKE URBAN database
import sys 
import os
import pdb

# Import arcpy
sys.path.append(r'C:\Program Files (x86)\ArcGIS\Desktop10.3\arcpy')
sys.path.append(r'c:\Program Files (x86)\ArcGIS\Desktop10.3\bin')
import arcpy

# Source and output path of database
in_dir  = os.path.abspath(r'C:\Users\Rasmus\Desktop\andreas')
out_dir = os.path.abspath(r'C:\Users\Rasmus\Desktop\andreas\test')

# Name of database
db_name = 'org.gdb'

# Path to old and new database
path_db     = os.path.join(in_dir, db_name)
path_new_db = os.path.join(out_dir, db_name)

# Delete any earlier versions of the output db
print('Deleting any earlier edits of the output database')
arcpy.Delete_management(path_new_db)

# Copy database to new location
print('Copying the old database')
if not arcpy.Exists(path_new_db):
    arcpy.Copy_management(path_db, path_new_db)
else:
    print('WARNING! Database already exist. Data will be overwritten')

# Preallocating in-memory
path_crsd = 'in_memory/CRSD'
path_crs  = 'in_memory/CRS'

# Copying features from db to in-memory
arcpy.CopyRows_management(path_new_db + os.sep + 'ms_CRSD', path_crsd)
arcpy.CopyRows_management(path_new_db + os.sep + 'ms_CRS', path_crs)

# Fields of interest in each data set
fields_crsd = ['crsid', 'hx', 'wz', 'RelRes', 'Sqn']
fields_crs  = ['MUID', 'TypeNo']

# Preallocating empty lists for CRS data
crsid, crsid_type, hx, wz, type_no = [[] for i in range(5)]

# Loading CRS coordinates
print('Loading CRS coordinates')  
with arcpy.da.SearchCursor(path_crsd, fields_crsd) as cursorno:
    for row in cursorno:
    	#print u'{0}, {1}, {2}'.format(row[0], row[1], row[2])
        crsid.append(row[0])
        hx.append(row[1])
        wz.append(row[2])

# Loading CRS ID and the corresponding type numbers
print('Loading CRS ID and type numbers') 
with arcpy.da.SearchCursor(path_crs, fields_crs) as cursorno:
    for row in cursorno:
        crsid_type.append(row[0])
        type_no.append(row[1])

# Create new list with the sorted type_no corresponding to crsid
# Used to match the type number of each cross section to the
# coordinates
type_no_sorted = []
for i in range(len(crsid)):
	for j in range(len(crsid_type)):
		if crsid_type[j] == crsid[i]:
			type_no_sorted.append(type_no[j])

# For some reason 3 of the CRSID's do not have a type_id...
print("WARNING! Some CRSID's do not have any type numbers!")
print("CRSID's with missing type number: {0}".format(crsid[-3:]))
crsid = crsid[:-3]

# Find the start and end index of each CRS by checking the CRSID
end_idx, start_idx, crsd_unique, type_no_sorted_unique = [[] for i in range(4)]
j = 0
for i in range(len(crsid) - 1):
	if crsid[i] != crsid[i + 1]:
		start_idx.append(j)
		end_idx.append(i)
		crsd_unique.append(crsid[i])
		type_no_sorted_unique.append(type_no_sorted[i])
		#print u'{0}, {1}'.format(crsid[i], type_no_sorted_unique[-1])
		j = i + 1

# Adds 1 meter to the largest and subtracts 1 meter from smallest 
# coordinate in the horizontal direction
x1, x2, y1, y2, crsid_new = [[] for i in range(5)]
for i in range(len(crsd_unique)):
	if type_no_sorted_unique[i] == 4:
		tmp = zip(hx[start_idx[i] : end_idx[i]], wz[start_idx[i] : end_idx[i]])
		tmp = sorted(tmp)
		# If the coordinates of the CRSID is empty, skip it
		if not tmp:
			print(crsd_unique[i])
			break
		#print(crsd_unique[i])
		#print(tmp)
		x1.append(min([x[0] for x in tmp]) - 1.0)
		x2.append(max([x[0] for x in tmp]) + 1.0)
		y1.append(100.0)
		y2.append(100.0)
		crsid_new.append(crsd_unique[i])
		# print '{0}, {1}'.format(crsid[i], x1[-1])

# Create insert cursor for table
rows = arcpy.InsertCursor(path_new_db + os.sep + 'ms_CRSD')

# Create new rows in the new db
print ('Writing data to new geodatabase')
for i in range(len(crsid_new)):
    row = rows.newRow()
    row.setValue(fields_crsd[0], crsid_new[i])
    row.setValue(fields_crsd[1], x1[i])
    row.setValue(fields_crsd[2], y1[i])
    row.setValue(fields_crsd[3], 1)
    row.setValue(fields_crsd[4], 0)
    rows.insertRow(row)

    row = rows.newRow()
    row.setValue(fields_crsd[0], crsid_new[i])
    row.setValue(fields_crsd[1], x2[i])
    row.setValue(fields_crsd[2], y2[i])
    row.setValue(fields_crsd[3], 1)
    row.setValue(fields_crsd[4], 99)
    rows.insertRow(row)

# Delete cursor and row objects to remove locks on the data
del row
del rows
