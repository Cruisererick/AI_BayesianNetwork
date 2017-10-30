import GetParameters
import numpy as np
import pandas as pd
import math
import re


def main():

    filemame = 'data5.csv'
    json = 'model3.json'
    dataframe = GetParameters.read_csv(filemame)
    json = GetParameters.read_json(json)
    parameters = get_parameters(dataframe)
    network = build_network(parameters, json)
    parameters_dict = calculate_probabilities(network, dataframe)
    order = fix_network(network)

    e = ["A", "B", "C", "D", "E"] # Parameters given
    # number = enumerate_ask(None, e, network, parameters_dict, order) # enumerate_ask (parameter, parameters given, network, probabilities of parameters, order of the network)
    # model_probability = model_fit(network, order, parameters_dict, dataframe) # Fit the model with the data
    # print(model_probability)


def fix_network(network):
    order = {}
    for item in network:
        string = order_network(network, item)
        order[item] = string
    network_order = []
    for x in range(0, len(order)):
        min_val = min(order, key=lambda k: len(order[k]))
        network_order.append(min_val)
        del order[min_val]

    return network_order


def order_network(network, item):

            try:
                string = ""
                item = str(item)
                item = re.sub('[\'\[\]]', '', item)
                A = str(network[item])
                A = re.sub('[\']', '', A)
                A = A.split(",")
                for x in range(0, len(A)):
                    A[x] = re.sub('[\'\[\]]', '', A[x])
                    B = order_network(network, A[x])
                    if B is not None:
                        string += A[x] + "," + B
                    else:
                        string += A[x]
                return string
            except:
                A = None
                B = None
                string = None
                return string


def build_network(parameters, json):
    network_dict = {}

    for parameter in parameters:
        try:
            sons = json[parameter]
            father = parameter
            for son in sons:
                if son in network_dict:
                    network_dict[son].append(father)
                else:
                    list = []
                    list.append(father)
                    network_dict[son] = list
            if father not in network_dict:
                list = []
                network_dict[father] = list
        except KeyError:
            pass

    return network_dict


def calculate_probabilities(network, dataframe):
    parameters_dict = {}

    for param in network:
        if len(network[param]) == 0:
            lookup = dataframe.groupby([param])[param].count()
            true = lookup[1]
            false = lookup[0]
            parameters_dict[param] = true / (true + false)
        else:
            lookup = dataframe.groupby([param, *network[param]])[param].count()
            iters = len(network[param]) * 2
            parentstate = [1] * len(network[param])
            for x in range(0, iters):
                true = lookup[1].copy()
                false = lookup[0].copy()
                if len(network[param]) > 1:
                    change = x % len(network[param])
                else:
                    change = 0

                iterfather = network[param][change]
                parentstate[change] = int(not parentstate[change])
                if "!" in iterfather:
                    iterfather = iterfather.replace("!", "")
                else:
                    iterfather = "!" + iterfather

                for y in range(0, len(network[param])):
                    try:
                        true = true[parentstate[y]]
                    except KeyError:
                        true = 0
                for y in range(0, len(network[param])):
                    try:
                        false = false[parentstate[y]]
                    except KeyError:
                        false = 0

                temp = network[param]
                temp[change] = iterfather
                parentsstring = str(temp).replace("[", "")
                parentsstring = parentsstring.replace("]", "")
                parentsstring = re.sub('[\']', '', parentsstring)

                parameters_dict[param + "|" + parentsstring] = true / (true + false)

    return parameters_dict


def get_parameters(dataframe):
    parameters = dataframe.keys()
    return parameters


def enumerate_ask(x, e, bn, know_prob, order):

    if x is not None:
        lookingfor = x
        result = []

        negative_bn = bn.copy()
        negative_order = order.copy()
        if "!" not in lookingfor:
            q = []
            q.append(lookingfor)
            q.append("!" + lookingfor)
            negative_bn["!" + lookingfor] = negative_bn[lookingfor]
            del negative_bn[lookingfor]
            for x in range(0, len(negative_order)):
                if negative_order[x] == lookingfor:
                    negative_order[x] = "!" + lookingfor
        else:
            q = []
            q.append(lookingfor.replace("!", ""))
            q.append(lookingfor)
            negative_bn[lookingfor] = negative_bn[lookingfor.replace("!", "")]
            del negative_bn[lookingfor.replace("!", "")]
            for x in range(0, len(negative_order)):
                if negative_order[x] == lookingfor.replace("!", ""):
                    negative_order[x] = lookingfor

        for value in q:
            if "!" in value:
                params = negative_bn.copy()
                order = negative_order.copy()
            else:
                params = bn.copy()
                order = order.copy()
            a = e.copy()
            a.append(value)
            number = enumerate_all(params, a, know_prob, order)
            result.append(number)

        x = result[0] + result[1]
        positive = result[0] / x
        negative = result[1] / x
        return [positive, negative]
    else:
        params = bn.copy()
        number = enumerate_all(params, e, know_prob, order)
        return number


def get_combinations(next_key, Y, e, know_prob):
    probo = 1
    fathers_list =[]
    if "!" not in next_key:
        if len(Y) > 0:
            for fathers in Y:
                if fathers in e:
                    fathers_list.append(fathers)
                    fathers_list.append(fathers)
                elif "!" + fathers in e:
                    fathers_list.append("!" + fathers)
                    fathers_list.append("!" + fathers)
                else:
                    fathers_list.append(fathers)
                    fathers_list.append("!" + fathers)
            combinations_done = {}
            for x in range(0, len(Y)):
                select = len(Y) % len(fathers_list)
                string_fathers = ""
                for y in range(0, select):
                    string_fathers += fathers_list[y * 2] + ", "
                string_fathers = string_fathers.strip(", ")

                if string_fathers in combinations_done:
                    pass
                else:
                    probo *= know_prob[next_key + "|" + string_fathers]
                    combinations_done[string_fathers] = probo
        else:
            probo = know_prob[next_key]
    return probo


def enumerate_all(params, e, know_prob, order):
    if not params:
        return 1
    next_key = next(iter(order))
    order.remove(next_key)
    Y = params[next_key]
    del params[next_key]
    next_key = re.sub('[\']', '', next_key)

    if "!" + next_key in e:
        next_key = "!" + next_key

    if next_key in e:
        if "!" not in next_key:
            probo = get_combinations(next_key, Y, e, know_prob)
            j = probo * enumerate_all(params, e, know_prob, order)
            return j
        else:
            temp = next_key.replace("!", "")
            probo = (1 - get_combinations(temp, Y, e, know_prob))
            j = probo * enumerate_all(params, e, know_prob, order)
            return j
    else:
        if "!" not in next_key:
            probo = get_combinations(next_key, Y, e, know_prob)
            a = e.copy()
            b = e.copy()
            aorder = order.copy()
            border = order.copy()
            a.append(next_key)
            b.append("!" + next_key)
            aparams = params.copy()
            bparams = params.copy()
            enum = enumerate_all(aparams, a, know_prob, aorder)
            A = (probo * enum)
            enum = enumerate_all(bparams, b, know_prob, border)
            B = (1 - probo) * enum
            return A + B
        else:
            temp = next_key.replace("!", "")
            probo = get_combinations(temp, Y, e, know_prob)
            a = e.copy()
            b = e.copy()
            aorder = order.copy()
            border = order.copy()
            a.append("!" + temp)
            b.append(temp)
            aparams = params.copy()
            bparams = params.copy()
            enum = enumerate_all(aparams, a, know_prob, aorder)
            A = (probo * enum)
            enum = enumerate_all(bparams, b, know_prob, border)
            B = (1 - probo) * enum
            return A + B


def model_fit(network, order, parameters_dict, dataframe):

    A = dataframe["A"].values.tolist()
    B = dataframe["B"].values.tolist()
    C = dataframe["C"].values.tolist()
    D = dataframe["D"].values.tolist()
    E = dataframe["E"].values.tolist()
    number = 0
    for x in range(0, len(A)):
        e = []
        if A[x] == "True":
            e.append("A")
        else:
            e.append("!A")

        if B[x] == "True":
            e.append("B")
        else:
            e.append("!B")

        if C[x] == "True":
            e.append("C")
        else:
            e.append("!C")

        if D[x] == "True":
            e.append("D")
        else:
            e.append("!D")

        if E[x] == "True":
            e.append("E")
        else:
            e.append("!E")

        number += math.log(enumerate_ask(None, e, network, parameters_dict, order))

        return number




if __name__ == '__main__':
    main()
