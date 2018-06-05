#!/usr/bin/env python

import rospy
import pandas as pd
from apriltags_ros.msg import AprilTagDetectionArray
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

from matplotlib.ticker import FuncFormatter

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


class tag_recognition_counter():
    def __init__(self):
        rospy.init_node('tag_recognition_counter', disable_signals=True)
        rospy.on_shutdown(self.saving_data)
        rospy.Subscriber("/usb_cam/tag_detections", AprilTagDetectionArray, self.counter)

        id_start = 116
        id_end = 150

        #self.id_index = range(id_start, id_end+1)
        self.id_index = [8, 140, 311, 583, 12, 32, 46, 51, 80, 129, 136]
        # Define a dataframe for saving reading.
        self.tag_df = pd.DataFrame()
        self.tag_df['tag_id'] = self.id_index
        self.tag_df.set_index('tag_id', inplace=True)
        self.count = 0
        rospy.spin()

    def counter(self, data):
        if self.count < 501:
            # Extract all the identified id
            tag_list = []
            for tag in data.detections:
                tag_list.append(tag.id)
            print(str(self.count) + ":  " + str(tag_list))

            tag_check = []
            for index in self.id_index:
                if index in tag_list:
                    tag_check.append(1)
                else:
                    tag_check.append(None)
            self.tag_df[self.count] = tag_check
            self.count += 1
            #print(self.tag_df.head())
        else:
            rospy.signal_shutdown('Got data for 30 seconds.')

    def saving_data(self):
        self.tag_df['sum'] = self.tag_df.sum(axis=1)
        self.tag_df.to_csv('comparison.csv', sep='\t', encoding='utf-8')

        # Create the formatter using the function to_percent. This multiplies all the
        # default labels by 100, making them all percentages
        formatter = FuncFormatter(to_percent)

        y_pos = np.arange(len(self.tag_df['sum']))*3
        plt.figure(figsize=(15, 10))
        plt.ylim(ymax=1)
        plt.xlim(xmax=y_pos[-1]+2)
        # Axis lable
        plt.title('AprilTag Identification Test')
        plt.xlabel('Tag ID')
        plt.ylabel('Identification Times in 30s.')

        barlist = plt.bar(y_pos, self.tag_df['sum']/500)
        # Colort mark the old tag.
        barlist[0].set_color('r')
        barlist[1].set_color('r')
        barlist[2].set_color('r')
        barlist[3].set_color('r')

        plt.xticks(y_pos, self.tag_df.index, rotation=30)
        # Set the formatter
        plt.gca().yaxis.set_major_formatter(formatter)
        plt.savefig('comparison.png')
        #plt.show()
        print "shutdown time!"


if __name__ == '__main__':
    try:
        tag_recognition_counter()
    except rospy.ROSInterruptException:
        pass