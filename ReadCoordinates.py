import arcpy
import datetime
import os
import re
from ScriptWorkingStatistics import timing


def calculateDistance(x1, y1, x2, y2, ProjectionFile):
    # dist = math.sqrt((x2-x1)**2 +(y2-y1)**2)
    pnt_Geometry = arcpy.PointGeometry(arcpy.Point(x1, y1), arcpy.SpatialReference(ProjectionFile))
    res = pnt_Geometry.angleAndDistanceTo(
        arcpy.PointGeometry(arcpy.Point(x2, y2), arcpy.SpatialReference(ProjectionFile)))
    return res


t = timing()
print "Script Has Been Initited"
## INPUTS
arcpy.env.overwriteOutput = True
ScriptRunFolder = u'C:\\Users\\HPZ640\\Desktop\\WORKLOAD\\DHI\\'
GeoDataBaseFolderLocation = ScriptRunFolder + 'Try.001.gdb'
CADFileLocation = ScriptRunFolder + 'kk.DWG'
ProjectionFile = ScriptRunFolder + '8111.prj'
CrossSectionIdentifier = u"PL_TOTFKM"
StreamIdentifier = "2"
ProjectionFile = "8111.prj"

## TODO  NCN file read
NameOftheCrossSection = "KesikKopru"
NCNFileLocation = "kk.NCN"
data = []
with open(NCNFileLocation, 'rb') as f:
    for line in f:
        tmp = []
        tmp2 = []
        tmp2 = (line.split())
        tmp.extend(tmp2[0].split('_'))
        tmp.extend([float(tmp2[1]), float(tmp2[2]), float(tmp2[3])])
        tmp[0] = int(tmp[0])
        tmp[1] = int(tmp[1])
        data.append(tmp)
f_data = sorted(data, key=lambda l: (l[0], l[1]), reverse=False)
cumulative = []
counter = 0
print t.incremental_runtime()
for en, points in enumerate(f_data):
    if f_data[en - 1][0] == points[0]:
        counter = counter + 1
    elif abs(f_data[en - 1][0] - points[0]) == 1:
        counter = 0
    if counter > 0:
        f_data[en].extend([f_data[en - 1][-1] + list(
            [calculateDistance(points[2], points[3], f_data[en - 1][2], f_data[en - 1][3], ProjectionFile)][0])[1]])
    else:
        f_data[en].extend([0])
print t.incremental_runtime()

ConvertedCADName = u'TempCad' + datetime.datetime.today().strftime("%y%m%d%H%M")
if not (arcpy.Exists(GeoDataBaseFolderLocation)):
    arcpy.CreateFileGDB_management(os.path.dirname(GeoDataBaseFolderLocation),
                                   os.path.basename(GeoDataBaseFolderLocation))
    print "A new filegeodabase has been created"
else:
    print "Geodatabase has Already Been Created"
print t.incremental_runtime()
arcpy.CADToGeodatabase_conversion(CADFileLocation, GeoDataBaseFolderLocation, ConvertedCADName, 1000)
print "CAD has been converted"
print t.incremental_runtime()
gdblocation = GeoDataBaseFolderLocation + "\\" + ConvertedCADName
liste_of_groupings = list(set(
    [row[1] for row in arcpy.da.SearchCursor(gdblocation + "\\Annotation", ["Layer", "TextString"]) if
     row[0].find(CrossSectionIdentifier) != -1]))
re_pattern = '(?=[0-9]{1,}\+).|(?<=[0-9]\+).+$'
p = re.compile(re_pattern)
a = []
for i in liste_of_groupings:
    m = p.findall(i)
    a.append([int(m[0]), float(m[1].replace('</UND>', ''))])
b = sorted(a, key=lambda l: (l[0], l[1]), reverse=False)
# arcpy.Delete_management(gdblocation)
print t.incremental_runtime()
f = open('DataExtract_' + datetime.datetime.today().strftime('%y%m%d%H%M') + '.txt', 'w')
for en, r in enumerate(list(set([row[0] for row in f_data]))):
    f.write("1\n%s\n" % NameOftheCrossSection)
    f.write("%20.3lf" % (b[en][0] * 1000 + b[en][1]))
    inner_temp = [row for row in f_data if row[0] == r]
    coordinates = [[row[2], row[3]] for row in inner_temp]
    arcpy.SelectLayerByLocation_management(gdblocation + "\\Annotation", "WITHIN_A_DISTANCE", arcpy.Multipoint(
        arcpy.Array([arcpy.Point(*coords) for coords in coordinates])), 5)
    coordinate_min = inner_temp[0][2:4]
    coordinate_max = inner_temp[-1][2:4]
    f.write("\nCOORDINATES\n     %s  %12.3lf %12.3lf %12.3lf %12.3lf\n" % (
    StreamIdentifier, coordinate_min[0], coordinate_min[1], coordinate_max[0], coordinate_max[1]))
    f.write(
        "FLOW DIRECTION\n    0      \nPROTECT DATA\n    0      \nDATUM\n      0.00\nRADIUS TYPE\n    0\nDIVIDE X-Section\n0\nSECTION ID\n")
    f.write("02_%02d\n" % r)
    f.write(
        "INTERPOLATED\n    0\nANGLE\n    0.00   0\nRESISTANCE NUMBERS\n   1  0     1.000     1.000     1.000    1.000    1.000\n")
    length = len(inner_temp)
    # print length, "02_" + str(r)
    f.write("PROFILE %9s \n" % length)
    for en_inner, inner in enumerate(inner_temp):
        for inn in [inner[-1], inner[-2]]:
            f.write('%10.3lf' % inn)
        if en_inner == 0:
            f.write('      1.000     <#%d>     0     0.000     0\n' % (1))
        elif en_inner == 1:
            f.write('      1.000     <#%d>     0     0.000     0\n' % (2))
        elif en_inner == 2:
            f.write('      1.000     <#%d>     0     0.000     0\n' % (4))
        else:
            f.write('      1.000     <#%d>     0     0.000     0\n' % (0))
    f.write('LEVEL PARAMS\n0  0    0.000  0    0.000  %d\n' % f_data[-1][0])
    f.write('*' * 31)
    f.write('\n')
f.close()
print "Script Has been Finalized"
print t.runtime()
