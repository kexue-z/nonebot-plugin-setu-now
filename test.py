from arclet.alconna import Alconna, Args, Option, action

a = Alconna(
    ["setu", "色图", "涩图", "来点色色", "色色", "涩涩", "来点色图"],
    Args["num", int, 1],
    Args["key", str, ""],
    Option("-r|--r18", default=False),
    Option("-t|--tag", Args["tag", str, ""], action=action.append),
)

r = a.parse("色图 -t 风景 -t 123")
print(r)

print(r.all_matched_args)

print(r.tag)
