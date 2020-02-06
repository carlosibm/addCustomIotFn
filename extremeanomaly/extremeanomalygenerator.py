import logging
import numpy as np
import pandas as pd
import datetime

from iotfunctions.base import BaseTransformer
from iotfunctions.ui import (UISingle, UIFunctionOutSingle, UISingleItem)
logger = logging.getLogger(__name__)

PACKAGE_URL = 'git+https://github.com/ankit-jha/addCustomIotFn@extreme_anomaly_package'

class ExtremeAnomalyGenerator(BaseTransformer):
    '''
    This function generates extreme anomaly.
    '''

    def __init__(self, input_item, factor, size, output_item):
        self.input_item = input_item
        self.output_item = output_item
        self.factor = int(factor)
        self.size = int(size)
        super().__init__()

    def execute(self, df):
        currentdt = datetime.datetime.now()
        logger.debug("-----------....")
        logger.debug(str(currentdt))
        timeseries = df.copy().reset_index()
        #Create a zero value series
        additional_values = pd.Series(np.zeros(timeseries[self.input_item].size),index=timeseries.index)
        timestamps_indexes = []
        logger.debug("--additional_values shape--{}".format(additional_values.shape))
        #Divide the timeseries in (factor)number of splits.Each split will have one anomaly
        for time_splits in np.array_split(timeseries,self.factor):
            start = time_splits.sample(1).index[0]
            timestamps_indexes.append(start)
        logger.debug("--timestamps --{}".format(timestamps_indexes))
        #Create extreme anomalies in every split
        for start  in timestamps_indexes:
            local_std = timeseries[self.input_item].iloc[max(0, start - 10):start + 10].std()
            logger.debug("--local_std --{}".format(local_std))
            logger.debug("--additional_values before --{}".format(additional_values.iloc[start]))
            additional_values.iloc[start] += np.random.choice([-1, 1]) * self.size * local_std
            logger.debug("--additional_values after --{}".format(additional_values.iloc[start]))
            timeseries[self.output_item] = additional_values + timeseries[self.input_item]

        timeseries.set_index(df.index.names,inplace=True)
        logger.debug("-----------....")
        logger.debug(str(currentdt))
        return timeseries

    @classmethod
    def build_ui(cls):
        inputs = []
        inputs.append(UISingleItem(
                name='input_item',
                datatype=float,
                description='Item to base anomaly on'
                                              ))

        inputs.append(UISingle(
                name='factor',
                datatype=int,
                description='No. of extreme anomalies to be created'
                                              ))

        inputs.append(UISingle(
                name='size',
                datatype=int,
                description='Size of extreme anomalies to be created. e.g. 10 will create 10x size extreme anomaly compared to the normal variance'
                                              ))

        outputs = []
        outputs.append(UIFunctionOutSingle(
                name='output_item',
                datatype=float,
                description='Generated Item With Extreme anomalies'
                ))
        return (inputs, outputs)
