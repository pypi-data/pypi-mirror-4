import json
import os


from specs import Spec

specspath = os.path.join(*os.path.split(__file__)[:-1] + ('specs.mspecs',))

rawspecs = json.load(open(specspath))

specs = []
for spec in rawspecs:
    specs.append(Spec(spec["spec"], spec["command"]))


def add():
    name = raw_input("Name?")
    spec = raw_input("Spec?")
    command = raw_input("Command?")
    blocktype = raw_input("Type?")
    while blocktype not in ["stack", "reporter"]:
        blocktype = raw_input("Invalid type! (stack/reporter/cap)\nType:")
    rawspecs.append({'name': name, 'spec': spec, 'command': command,
                  'type': blocktype})


def save():
    with open(specspath, 'w') as file:
        json.dump(rawspecs, file, indent=2, sort_keys=True)


if __name__ == "__main__":
    for spec in rawspecs:
        print spec["spec"], "executes", spec["command"]
    while raw_input("Continue? (y)") in ["y", "Y"]:
        add()
    save()
