import GetParameters
import numpy as np
import pandas as pd
import re


def main():

    filemame = 'C://Users//Juan//Desktop//AI network data//data1.csv'
    json = 'C://Users//Juan//Desktop//AI network data//bn1.json'
    dataframe = GetParameters.read_csv(filemame)
    json = GetParameters.read_json(json)
    parameters = get_parameters(dataframe)
    network = build_network(parameters, json)

    parameters_dict = calculate_probabilities(network, dataframe)
    e = ["Good Engine", "Working Air Conditioner"]

    enumerate_ask("High Car Value", e, network, parameters_dict)




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


def enumerate_ask(x, e, bn, know_prob):

    lookingfor = x


    result = []

    negative_bn = bn.copy()
    if "!" not in lookingfor:
        q = []
        q.append(lookingfor)
        q.append("!" + lookingfor)
        negative_bn["!" + lookingfor] = negative_bn[lookingfor]
        del negative_bn[lookingfor]
    else:
        q = []
        q.append(lookingfor.replace("!", ""))
        q.append(lookingfor)
        negative_bn[lookingfor] = negative_bn[lookingfor.replace("!", "")]
        del negative_bn[lookingfor.replace("!", "")]


    for value in q:
        if "!" in value:
            params = negative_bn.copy()
        else:
            params = bn.copy()
        a = e.copy()
        a.append(value)
        number = enumerate_all(params, a, know_prob)
        result.append(number)

    x = result[0] + result[1]
    positive = result[0] / x
    negative = result[1] / x
    print("pos" + ":" + str(positive) + "\n" + "neg" + ":" + str(negative))


def enumerate_all(params, e, know_prob):
    if not params:
        return 1
    next_key = next(iter(params))
    Y = params[next_key]
    del params[next_key]
    next_key = re.sub('[\']', '', next_key)

    if "!" + next_key in e:
        next_key = "!" + next_key

    if next_key in e:
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
                combinatios_done = {}
                for x in range(0, len(Y)):
                    select = len(Y) % len(fathers_list)
                    string_fathers = ""
                    for y in range(0, select):
                        string_fathers += fathers_list[y * 2] + ", "
                    string_fathers = string_fathers.strip(", ")

                    if string_fathers in combinatios_done:
                        pass
                    else:
                        probo *= know_prob[next_key + "|" + string_fathers]
                        combinatios_done[string_fathers] = probo
            else:
                probo = know_prob[next_key]
            j = probo * enumerate_all(params, e, know_prob)
            return j
        else:
            temp = next_key.replace("!", "")
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
                combinatios_done = {}
                for x in range(0, len(Y)):
                    select = len(Y) % len(fathers_list)
                    string_fathers = ""
                    for y in range(0, select):
                        string_fathers += fathers_list[y * 2] + ", "
                    string_fathers = string_fathers.strip(", ")
                    if string_fathers in combinatios_done:
                        pass
                    else:
                        probo *= (1 - know_prob[temp + "|" + string_fathers])
                        combinatios_done[string_fathers] = probo
            else:
                probo = 1 - know_prob[temp]
            j = probo * enumerate_all(params, e, know_prob)
            return j

    else:
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
                combinatios_done = {}
                for x in range(0, len(Y)):
                    select = len(Y) % len(fathers_list)
                    string_fathers = ""
                    for y in range(0, select):
                        string_fathers += fathers_list[y * 2] + ", "
                    string_fathers = string_fathers.strip(", ")
                    if string_fathers in combinatios_done:
                        pass
                    else:
                        probo *= know_prob[next_key + "|" + string_fathers]
                        combinatios_done[string_fathers] = probo
            else:
                probo = know_prob[next_key]
            a = e.copy()
            b = e.copy()
            a.append(next_key)
            b.append("!" + next_key)
            aparams = params.copy()
            bparams = params.copy()
            enum = enumerate_all(aparams, a, know_prob)
            A = (probo * enum)
            enum = enumerate_all(bparams, b, know_prob)
            B = (1 - probo) * enum
            return A + B
        else:
            temp = next_key.replace("!", "")
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
                combinatios_done = {}
                for x in range(0, len(Y)):
                    select = len(Y) % len(fathers_list)
                    string_fathers = ""
                    for y in range(0, select):
                        string_fathers += fathers_list[y * 2] + ", "
                    string_fathers = string_fathers.strip(", ")
                    if string_fathers in combinatios_done:
                        pass
                    else:
                        probo *= (1 - know_prob[temp + "|" + string_fathers])
                        combinatios_done[string_fathers] = probo
            else:
                probo = 1 - know_prob[temp]
            a = e.copy()
            b = e.copy()
            a.append("!" + temp)
            b.append(temp)
            aparams = params.copy()
            bparams = params.copy()
            enum = enumerate_all(aparams, a, know_prob)
            A = (probo * enum)
            enum = enumerate_all(bparams, b, know_prob)
            B = (1 - probo) * enum
            return A + B




if __name__ == '__main__':
    main()
