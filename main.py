import GetParameters
import pandas as pd



def main():

    filemame = 'C://Users//Juan//Desktop//AI network data//data1.csv'
    dataframe = GetParameters.read_csv(filemame)

    parameters = get_parameters(dataframe)
    calculate_pro(parameters, dataframe)


def calculate_pro(parameters, dataframe):
    parameters_Dict = {}

    x = dataframe.groupby(parameters[0])[parameters[0]].count()
    high_milage_true = x[0]/(x[0] + x[1])
    print(high_milage_true)


    x = dataframe.groupby(parameters[2])[parameters[2]].count()
    air_working_true = x[0]/(x[0] + x[1])
    print(air_working_true)


    x = dataframe.groupby([parameters[1], parameters[0]])[parameters[1]].count()
    true_false = x.loc[[(1, 0)]]
    false_false = x.loc[[(0, 0)]]
    false_true = x.loc[[(0, 1)]]
    true_true = x.loc[[(1, 1)]]

    engine_working_mt = true_false[1][0] / (true_false[1][0] + false_false[0][0])
    engine_working_mf = true_true[1][1] / (true_true[1][1] + false_true[0][1])
    print(engine_working_mt)
    print(engine_working_mf)

    x = dataframe.groupby([parameters[3], parameters[1], parameters[2]])[parameters[3]].count()
    true_true_true = x.loc[[(1, 1, 1)]]
    false_true_true = x.loc[[(0, 1, 1)]]

    true_true_false = x.loc[[(1, 1, 0)]]
    false_true_false = x.loc[[(0, 1, 0)]]

    true_false_true = x.loc[[(1, 0, 1)]]
    false_false_true = x.loc[[(0, 0, 1)]]

    highvalue_et_at = true_true_true[1][1][1] / (true_true_true[1][1][1] + false_true_true[0][1][1])
    highvalue_et_af = true_true_false[1][1][0] / (false_true_false[0][1][0] + true_true_false[1][1][0])
    highvalue_ef_at = true_false_true[1][0][1] / (true_false_true[1][0][1] + false_false_true[0][0][1])
    highvalue_ef_af = 0

    print(highvalue_et_at)
    print(highvalue_et_af)
    print(highvalue_ef_at)
    print(highvalue_ef_af)






def get_parameters(dataframe):
    parameters = dataframe.keys()
    return parameters


if __name__ == '__main__':
    main()
