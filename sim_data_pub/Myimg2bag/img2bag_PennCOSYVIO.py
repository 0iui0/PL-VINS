import os
import roslib
import rospy
import sys
from ros import rosbag

roslib.load_manifest('sensor_msgs')
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3

# import ImageFile

from cv_bridge import CvBridge
import cv2


def CompSortFileNamesNr(f):
    g = os.path.splitext(os.path.split(f)[1])[0]  # get the file of the
    numbertext = ''.join(c for c in g if c.isdigit())
    return int(numbertext)


def ReadImages(filename):
    '''Generates a list of files from the directory'''
    print("Searching directory %s" % dir)
    all = []
    left_files = []
    right_files = []
    files = os.listdir(filename)
    for f in sorted(files):
        if os.path.splitext(f)[1] in ['.bmp', '.png', '.jpg', '.pgm']:
            '''
            if 'left' in f or 'left' in path:
                left_files.append(os.path.join(path, f))
            elif 'right' in f or 'right' in path:
                right_files.append(os.path.join(path, f))
            '''
            all.append(os.path.join(filename, f))
    return all


def ReadIMU(filename):
    '''return IMU data and timestamp of IMU'''
    file = open(filename, 'r')
    all = file.readlines()
    timestamp = []
    imu_data = []
    for f in all:
        s = f.rstrip('\n')
        #	print s
        #	print s.split()
        s = ' '.join(s.split());
        line = s.split(' ')
        print
        line
        timestamp.append(line[0])
        imu_data.append(line[1:])
    return timestamp, imu_data


def CreateBag(args):  # img,imu, bagname, timestamps
    '''read time stamps'''
    imgs = ReadImages(args[0])
    imagetimestamps = []
    imutimesteps, imudata = ReadIMU(args[1])  # the url of  IMU data
    file = open(args[3], 'r')
    all = file.readlines()
    for f in all:
        imagetimestamps.append(f.rstrip('\n'))
    #    print imagetimestamps
    #    print imutimesteps
    file.close()
    '''Creates a bag file with camera images'''
    if not os.path.exists(args[2]):
        os.system(r'touch %s' % args[2])
    bag = rosbag.Bag(args[2], 'w')

    try:
        for i in range(len(imudata)):
            imu = Imu()
            angular_v = Vector3()
            linear_a = Vector3()
            angular_v.x = float(imudata[i][3])
            angular_v.y = float(imudata[i][4])
            angular_v.z = float(imudata[i][5])
            linear_a.x = float(imudata[i][0])
            linear_a.y = float(imudata[i][1])
            linear_a.z = float(imudata[i][2])
            imuStamp = rospy.rostime.Time.from_sec(float(imutimesteps[i]))
            imu.header.stamp = imuStamp
            imu.angular_velocity = angular_v
            imu.linear_acceleration = linear_a

            bag.write("IMU/imu_raw", imu, imuStamp)

        for i in range(len(imgs)):
            print("Adding %s" % imgs[i])
            fp = open(imgs[i], "r")
            Stamp = rospy.rostime.Time.from_sec(float(imagetimestamps[i]))

            frame = cv2.imread(imgs[i], 0)
            cb = CvBridge()
            img_ros = cb.cv2_to_imgmsg(frame, encoding='mono8')
            img_ros.header.stamp = Stamp
            img_ros.header.frame_id = "camera"
            bag.write('camera/image_raw', img_ros, Stamp)
            # cv2.imshow("img",img)
            # cv2.waitKey(0)

            ## python PIL image lib
            # p = ImageFile.Parser()
            # '''read image size'''
            # imgpil = ImagePIL.open(imgs[0])
            #
            # width, height = imgpil.size
            # print "size:", width, height
            #
            # while 1:
            #     s = fp.read(1024)
            #     if not s:
            #         break
            #     p.feed(s)
            #
            # im = p.close()
            #
            # '''set image information '''
            # Img = Image()
            #
            # Img.header.stamp = Stamp
            # Img.height = height
            # Img.width = width
            # Img.header.frame_id = "camera"
            #
            # '''for rgb8'''
            # # Img.encoding = "rgb8"
            # # Img_data = [pix for pixdata in im.getdata() for pix in pixdata]
            # # Img.step = Img.width * 3
            #
            # '''for mono8'''
            # Img.encoding = "mono8"
            # Img_data = [pix for pixdata in [im.getdata()] for pix in pixdata]
            # Img.step = Img.width
            #
            # Img.data = Img_data
            # bag.write('camera/image_raw', Img, Stamp)
    finally:
        bag.close()


if __name__ == "__main__":
    print(sys.argv)
    CreateBag(sys.argv[1:])
