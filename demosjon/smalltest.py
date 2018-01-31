import json
import pprint

x = "{'\n' 1:{2:[2,3,4],4:[2,3,4]}}"
# data = json.loads(x)
data = json.loads(x)
# print(pprint.pprint(x,depth = 1))
print(data)
# with open('test.json' ,'w') as f:
# 	json.dump(x, f,indent = 4)