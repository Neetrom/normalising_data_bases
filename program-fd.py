from copy import copy

class Object_for_the_sake_of_it:
    def __init__(self, atributes, relations):
        self.atributes = []
        self.initialize_atributes(atributes)
        self.relation_dict = {}
        self.get_relations_into_a_dict(relations)
        self.closures = {}
        self.potential_keys = []
        self.key_atributes = []
        self.not_key_atributes = []

        self.left_side_atributes = []
        self.get_atributes_that_could_be_in_key()

        self.generate_closures([], len(self.atributes))
        self.get_key_candidates()
        self.get_key_atributes_and_not()
        self.generate_F_min()

    def initialize_atributes(self, atributes):
        atributes = atributes.split(",")
        for atr in atributes:
            self.atributes.append(atr.strip())
        self.atributes.sort()

    def get_atributes_that_could_be_in_key(self):
        for left_side, val in self.relation_dict.items():
            for atr in left_side.split(","):
                if atr not in self.left_side_atributes:
                    self.left_side_atributes.append(atr)

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
            rel = rel.split(",")
            rel.sort()
            rel = self.stringify(rel)
            ehh = self.relation_dict.get(rel, [])
            ehh.extend(value)
            self.relation_dict[rel] = ehh

    def stringify(self, list):
        list.sort()
        r_string = ""
        for item in list:
            r_string = r_string + "," + item
        return r_string[1:]

    def generate_closures(self, possible_key, depth):
        if depth <= 0: 
            return
        for atr in self.left_side_atributes:
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
            if len(temp_list) == len(self.atributes):
                depth = 0
            self.closures[self.stringify(new_key)] = temp_list
            self.generate_closures(copy(new_key), depth - 1)
    
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
    
    def get_atributes_from_immediate_relations(self, key):
        atr_list = []
        to_add = self.relation_dict[key]
        atr_list.extend(to_add)
        atr_list.extend(key.split(","))

        return atr_list

    def synthesis_to_n3(self):
        R_dict = {}
        for item in self.relation_dict.keys():
            R_dict[item] = self.get_atributes_from_immediate_relations(item)
            R_dict[item].sort()

        keys_to_remove = []

        for item in self.relation_dict.keys():
            second_closure = self.get_atributes_from_immediate_relations(item)
            for item2 in self.relation_dict.keys():
                if item == item2:
                    continue
                if item2 in keys_to_remove:
                    continue
                first_closure = self.get_atributes_from_immediate_relations(item2)
                if self.is_sublist(first_closure, second_closure):
                    keys_to_remove.append(item2)
        
        for key in keys_to_remove:
            R_dict.pop(key)
        
        for key in self.potential_keys:
            for right_side in self.relation_dict.values():
                if self.is_sublist(key.split(","), right_side):
                    break
            else:
                R_dict[key] = self.relation_dict.get(key,[])
                break
    
        PN3_relations = {}
        for left_side, right_side in R_dict.items():
            if right_side:
                r_side_string = self.stringify(right_side)
                PN3_relations[r_side_string] = []
                for atr in self.relation_dict[left_side]:
                    add_relation = {left_side : atr}
                    PN3_relations[r_side_string].append(add_relation)
                
                for item in right_side:
                    if item in left_side:
                        continue
                    for atr in self.relation_dict.get(item, []):
                        if atr in left_side.split(","):
                            PN3_relations[r_side_string].append({item : atr})
            else:
                PN3_relations[left_side] = []
        
        print(PN3_relations)


    def redundant_relation(self, left_side, right_side):
        relations_without_changes = self.closures[left_side]
        for atribute in copy(right_side):
            self.relation_dict[left_side].remove(atribute)
            relations_with_one_deleted = self.atributes_from_key(left_side.split(","))
            relations_without_changes.sort()
            relations_with_one_deleted.sort()
            self.relation_dict[left_side].append(atribute)
            if relations_without_changes == relations_with_one_deleted:
                return atribute

    def remove_items_from_relation_dict(self, remove_dict):
        for item, val in remove_dict.items():
            self.relation_dict.get(item).remove(val)
            if not self.relation_dict[item]:
                self.relation_dict.pop(item)

    def generate_F_min(self):
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

        self.remove_items_from_relation_dict(remove_dict)
        for item, val in self.relation_dict.items():
            redundant = self.redundant_relation(item, val)
            if not redundant:
                continue
            self.relation_dict[item].remove(redundant)
            if not self.relation_dict[item]:
                self.relation_dict.pop(item)
    
    def print_F_min(self):
        for item, val in self.relation_dict.items():
            for r in val:
                print(f"{item}: {r}")
    
    def get_key_candidates(self):
        keys = []
        for item, val in self.closures.items():
            val.sort()
            if val == self.atributes:
                keys.append(item)
        if not keys:
            self.potential_keys = self.atributes
            return
        min_size = len(keys[0])
        for item in keys:
            if item.count(",") < min_size:
                min_size = item.count(",")
        for item in keys:
            if item.count(",") == min_size:
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

    def second_normal(self):
        for key_atribute in self.key_atributes:
            atributes_from_key_atribute = self.closures[key_atribute]
            for atr in self.not_key_atributes:
                if atr in atributes_from_key_atribute:
                    return False
        return True
    
    def third_normal(self):
        if self.atributes_from_key(self.not_key_atributes):
            return False
        else:
            return True

    def is_sublist(self, list, list2):
        if not list or not list2:
            return False
        for item in list:
            if item not in list2:
                return False
        return True
    
atributes = "pesel, pakiet, imię, nazwisko, cena, rodzaj"
relations = "pesel -> imię, nazwisko;pakiet -> cena, rodzaj"


solver = Object_for_the_sake_of_it(atributes, relations)
solver.second_normal()
solver.synthesis_to_n3()
# TODO: algorytm syntezy

