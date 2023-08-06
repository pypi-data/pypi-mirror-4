# mlocs - sensible location storage...
# 
# mlocs provides a simple, yet effective location hashing algorithm.
# it's not super precise (> 750m.) but it provides perfect results.
#
# There are 5 levels available.
# Lvl 1 : World Scope
# Lvl 2 : Region Scope
# Lvl 3 : Metro Scope
# Lvl 4 : City Scope
# Lvl 5 : I See You
#
# toMaiden([lat, lon], level) returns a char (len = lvl*2)
# toLoc(mloc) takes any string and returns topleft [lat,lon] within mloc

