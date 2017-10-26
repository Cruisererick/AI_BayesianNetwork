import GetParameters
import numpy as np
import pandas as pd


def main():

    filemame = 'C://Users//Juan//Desktop//AI network data//data1.csv'
    json = 'C://Users//Juan//Desktop//AI network data//bn1.json'
    dataframe = GetParameters.read_csv(filemame)
    json = GetParameters.read_json(json)
    parameters = get_parameters(dataframe)
    network = build_network(parameters, json)
    parameters_dict = calculate_probabilities(network, dataframe)

    for ele in parameters_dict:
        print(ele)
        print(parameters_dict[ele])


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

                parameters_dict[param + "|" + parentsstring] = true / (true + false)

    return parameters_dict


def get_parameters(dataframe):
    parameters = dataframe.keys()
    return parameters


if __name__ == '__main__':
    main()
