from copy import copy

class Object_for_the_sake_of_it:
    def __init__(self, atributes, relations):
        self.atributes = []
        self.initialize_atributes(atributes)
        self.relation_dict = {}
        self.get_relations_into_a_dict(relations)
        self.all_keys = {}
        self.potential_keys = []
        self.key_atributes = []
        self.not_key_atributes = []

        self.get_all_keys([], len(self.atributes))
        self.get_key_candidates()
        self.get_key_atributes_and_not()

    def initialize_atributes(self, atributes):
        atributes = atributes.split(",")
        for atr in atributes:
            self.atributes.append(atr.strip())
        self.atributes.sort()

    def get_relations_into_a_dict(self, relations):
        relations = relations.split(";")
        for relation in relations:
            relation = relation.split("->")
            value = []
            for item in relation[1].split(","):
                item = item.strip()
                value.append(item)
            for item in relation[0].split(","):
                item = item.strip()
                if item in value:
                    value.remove(item)
            rel = relation[0].strip()
            ehh = self.relation_dict.get(rel, [])
            ehh.extend(value)
            self.relation_dict[rel] = ehh

    def stringify(self, list):
        list.sort()
        r_string = ""
        for item in list:
            r_string = r_string + "," + item
        return r_string[1:]

    def get_all_keys(self, possible_key, depth):
        if depth <= 0: 
            return
        for atr in self.atributes:
            new_key = copy(possible_key)
            if atr in new_key:
                continue
            new_key.append(atr)
            new_key.sort()
            temp_list = copy(new_key)
            count = len(temp_list) - 1
            while True:
                count = len(temp_list)
                for item, val in self.relation_dict.items():
                    start_over_flag = False
                    for left_side in item.split(","):
                        if left_side not in temp_list:
                            break
                    else:
                        for v in val:
                            if v not in temp_list:
                                temp_list.append(v)
                                start_over_flag = True
                    if start_over_flag:
                        break
                if count == len(temp_list):
                    break
            temp_list.sort()
            if temp_list == self.atributes:
                depth = 0
            self.all_keys[self.stringify(new_key)] = temp_list
            self.get_all_keys(copy(new_key), depth - 1)
    
    def atributes_from_key(self, key):
        temp_list = copy(key)
        count = len(temp_list) - 1
        while True:
            count = len(temp_list)
            for item, val in self.relation_dict.items():
                for left_side in item.split(","):
                    if left_side not in temp_list:
                        break
                else:
                    for v in val:
                        if v not in temp_list:
                            temp_list.append(v)
            if count == len(temp_list):
                break
        return temp_list

    def get_min_F(self):
        remove_dict = {}
        for item, val in self.relation_dict.items():
            for item2, val2 in self.relation_dict.items():
                if item == item2:
                    continue
                if item not in item2:
                    continue
                for v in val:
                    if v in val2:
                        remove_dict[item2] = v
        for item, val in remove_dict.items():
            self.relation_dict.get(item).remove(val)
            if not self.relation_dict[item]:
                self.relation_dict.pop(item)
        for item, val in self.relation_dict.items():
            for r in val:
                print(f"{item}: {r}")
    
    def get_key_candidates(self):
        keys = []
        for item, val in self.all_keys.items():
            val.sort()
            if val == self.atributes:
                keys.append(item)
        if not keys:
            self.potential_keys = self.atributes
            return
        min_size = len(keys[0])
        for item in keys:
            if len(item) < min_size:
                min_size = len(item)
        for item in keys:
            if len(item) == min_size:
                self.potential_keys.append(item)
    
    def get_key_atributes_and_not(self):
        for item in self.potential_keys:
            for key in item.split(","):
                if key not in self.key_atributes:
                    self.key_atributes.append(key)
        self.key_atributes.sort()
        for item in self.atributes:
            if item not in self.key_atributes:
                self.not_key_atributes.append(item)
        self.not_key_atributes.sort()


atributes = "A, B, C, D, E, F, G, H, I, J, XD"

relations = "A   -> D,E;B   -> F;D   -> I,J;C,G -> H;B   -> XD,D;XD  -> A,B"
solver = Object_for_the_sake_of_it(atributes, relations)

solver.get_min_F()
# TODO: Fmin
#wszystkie zależności funkcyjne w 𝓕min mają jednoelementowe prawe strony (są w tzw. postaci kanonicznej),
# po usunięciu dowolnej zależności funkcyjnej z 𝓕min, wynikowy zbiór nie będzie już bazą,
# jeśli z dowolnej zależności funkcyjnej z 𝓕min usuniemy jeden lub kilka atrybutów z lewej strony zależności, to wynik nie będzie bazą.



