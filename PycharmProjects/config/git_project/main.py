import os
import zlib


class VisualizerGit:

    def __init__(self):
        self.repository = os.getcwd()
        self.commits = []
        self.trees = []
        self.blobs = []
        self.nodes = []
        self.graph = []

    def get_objects(self):
        path = self.repository + "\\.git\\objects"
        for i in os.walk(path):
            obj = os.path.split(i[0])
            folder = obj if len(obj[-1]) == 2 else None
            if folder is not None:
                for j in (i[-1]):
                    file_path = os.path.join(folder[0], folder[1]) + "\\" + j
                    info = zlib.decompress(open(file_path, 'rb').read())
                    what = info.split()[0].decode('utf-8')
                    if what == "blob":
                        blob = {"type": info.split()[0].decode('utf-8'),
                                "name": folder[-1] + j,
                                "text": info.split()[1].decode('utf-8')[info.split()[1].find(b'\x00') + 1:]}
                        self.blobs.append(blob)
                    elif what == "tree":
                        tree = {"type": info.split()[0].decode('utf-8'),
                                "name": folder[-1] + j}
                        files = []
                        for file in info.split(b" ")[2:]:
                            file_way = path + "\\" + file[file.find(b'\x00') + 1:][0:20].hex()[0:2] + \
                                       "\\" + file[file.find(b'\x00') + 1:][:20].hex()[2:]
                            file_info = zlib.decompress(open(file_way, 'rb').read())
                            file_what = file_info.split()[0].decode('utf-8')
                            files.append({
                                "type": file_what,
                                "name": file[:file.find(b'\x00')].decode('utf-8'),
                                "path": file[file.find(b'\x00') + 1:][:20].hex()
                            })
                        tree["files"] = files
                        self.trees.append(tree)
                    elif what == "commit":
                        content = info.split(
                            b'\n')
                        commit = {"type": content[0].split()[0].decode('utf-8'),
                                  "name": folder[-1] + j,
                                  "parent": []}
                        for u in range(len(content) - 3):
                            if b"tree" in content[u]:
                                commit["tree"] = content[u].split()[-1].decode('utf-8')
                            elif b"parent" in content[u]:
                                parent = content[u].split()[1:]
                                for k in range(len(parent)):
                                    commit["parent"].append(parent[k].decode('utf-8'))
                        for u in range(len(content[-3:])):
                            if content[-3:][u] != b"":
                                commit["text"] = content[-3:][u].decode('utf-8')
                                break
                        self.commits.append(commit)

    def link_objects(self):
        union = self.commits + self.trees + self.blobs
        for i in range(len(union)):
            node = {}
            name = str(i + 1)
            node["obj"] = union[i]["name"]
            node["name"] = name
            node["type"] = union[i]["type"]
            node["parent"] = []
            if union[i]["type"] == "commit":
                node["parent"] = union[i]["parent"]
                node["text"] = f"Commit: {union[i]['text']}"
            elif union[i]["type"] == "tree":
                tree_name = ""
                for commit in self.commits:
                    if commit["tree"] == union[i]["name"]:
                        node["parent"].append(commit["name"])
                for tree in self.trees:
                    for file in tree["files"]:
                        if file["path"] == union[i]["name"]:
                            node["parent"].append(tree["name"])
                            tree_name = file["name"]
                            break
                node["text"] = f"Tree: {tree_name if tree_name != '' else 'tree'}"
            elif union[i]["type"] == "blob":
                file_name = ""
                for tree in self.trees:
                    for file in tree["files"]:
                        if file["path"] == union[i]["name"]:
                            node["parent"].append(tree["name"])
                            file_name = file["name"]
                            break
                node["text"] = f"{file_name}"
                node["inside"] = "Blob: " + "'" + union[i]["text"] + "'" if len(union[i]["text"]) != 0 else "Blob: ''"
            self.nodes.append(node)

    def create_graph(self):
        self.graph = 'digraph G {\n edge[color="gray"]\n'
        for node in range(len(self.nodes)):
            if "Commit" in self.nodes[node]["text"]:
                self.graph += f' {self.nodes[node]["name"]}[label="{self.nodes[node]["obj"][0:6]}\\n{self.nodes[node]["text"]}", shape="rectangle", style="filled", color="#EFDE74"]\n'
            elif "Tree" in self.nodes[node]["text"]:
                self.graph += f' {self.nodes[node]["name"]}[label="{self.nodes[node]["obj"][0:6]}\n{self.nodes[node]["text"]}", shape="rectangle", style="filled", color="#7bb2f9"]\n'
            else:
                self.graph += f' {self.nodes[node]["name"]}[label="{self.nodes[node]["obj"][0:6]}\n{self.nodes[node]["inside"]}", shape="rectangle", style="filled", color="#90ef74"]\n'
        for node in self.nodes:
            parents = []
            for i in range(len(node["parent"])):
                for j in self.nodes:
                    if j["obj"] == node["parent"][i]:
                        parents.append(j["name"])
            for i in range(len(parents)):
                if "Commit" in node["text"]:
                    self.graph += f' {node["name"]} -> {parents[i]}\n'
                elif "Tree" in node["text"]:
                    self.graph += f' {parents[i]} -> {node["name"]}\n'
                else:
                    self.graph += f' {parents[i]} -> {node["name"]} [taillabel = "{node["text"]}", fontsize="12"]\n'
        self.graph += "}"


if __name__ == '__main__':
    git = VisualizerGit()
    git.get_objects()
    git.link_objects()
    git.create_graph()
    print(git.graph)
