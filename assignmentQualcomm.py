import json
import matplotlib.pyplot as plt
import numpy as np
import math



def readfile(file_path):
    loc_x = []
    loc_y = []
    loc_z = []
    T =[]

    with open(file_path, 'r') as file:
        lines = file.readlines()


    for line_number, line in enumerate(lines, start=1):
        try:
            data = json.loads(line)
            Tsc = data['Tsc']
            time = data['t']


            loc_x.append(Tsc[0])
            loc_y.append(Tsc[1])
            loc_z.append(Tsc[2])
            T.append(time)

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON object {line_number}: {e}")
    return loc_x,loc_y,loc_z,T

def eval(loc_X,loc_Y,loc_Z,theta,T,thresholdDegree,flag):
    cordsToView =50
    dervativeTheta = abs(np.gradient(np.array(theta)))
    # theta = [x for x in theta if not math.isnan(x)]
    timeStamps =[]
    jitterLoc = []


    if flag == 1:

        fig = plt.figure(figsize=(18, 5))
        ax_3d = fig.add_subplot(1, 3, 1, projection='3d')
        ax_2d = fig.add_subplot(1, 3, 2)
        ax_2d1 = fig.add_subplot(1, 3, 3)

        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Z')

        ax_2d.set_xlabel('time index')
        ax_2d.set_ylabel('relative change in orientation of velocity vector')
        ax_2d1.set_title('vector representation')



    for i in range(1,len(theta)):

        val = theta[i-1]
        delta = abs(theta[i-1] -theta[i])

        if delta>30 and delta <150:
            jitterLoc.append([loc_X[i-1],loc_Y[i-1],loc_Z[i-1]])

        is_in_range = np.any((val >= (180-thresholdDegree)) & (val <= (180+thresholdDegree)))

        if is_in_range:
           if val >= (180-thresholdDegree) and val <= (180+thresholdDegree):
               val = abs(180-val)

        # Convert angle from degrees to radians
        angle_radians = np.radians(val)
        x_component = np.cos(angle_radians)
        y_component = np.sin(angle_radians)
        cords = np.arange(i-1,i+2)

        if val<= thresholdDegree:
            for j in range(len(cords)):
                timeStamps.append(T[cords[j]])
            motion = "linear"
            col = "green"
        else:
            motion ="non-linear"
            col ="red"

        colors = np.random.rand(1, 3)
        if flag == 1:
            if i % cordsToView == 0:
                ax_3d.clear()
            ax_2d.plot(theta[0:i],color='black',linestyle='--',marker='o')
            ax_3d.plot(loc_X[i - 1:i + 2], loc_Y[i - 1:i + 2], loc_Z[i - 1:i + 2], linestyle='--', marker='o', c=colors, )
            ax_2d.set_xlim(i-19, i+2)  # Example limits, adjust as needed
            ax_2d1.quiver(0, 0, x_component, y_component, angles='xy', scale_units='xy', scale=1,headwidth=10, headlength=10)
            ax_3d.set_title(motion, color=col)
            ax_2d1.set_title('vector representation')
            plt.waitforbuttonpress()
            # plt.pause(.001)
            ax_2d1.clear()
            print(i)
    return timeStamps,jitterLoc


def computeVelocity(loc_X,loc_Y,loc_Z):
    velX = []
    velY = []
    velZ = []
    for i in range(0,len(loc_X)-1):
        velX.append([loc_X[i+1]-loc_X[i]])
        velY.append([loc_Y[i + 1] - loc_Y[i]])
        velZ.append([loc_Z[i + 1] - loc_Z[i]])

    return velX,velY,velZ

def computeTheta(velX,velY,velZ):
    theta = []
    for i in range(0,len(velX) - 1):
        vec1 = np.array([velX[i],velY[i],velZ[i]]).reshape(-1)
        vec2 = np.array([velX[i+1],velY[i+1],velZ[i+1]]).reshape(-1)
        phi = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        angleRad = math.degrees(np.arccos(np.clip(phi, -1.0, 1.0)))
        theta.append((angleRad))
    return theta


def main():
    file_path = 'test.json'
    loc_X,loc_Y,loc_Z,T =readfile(file_path)
    velX,velY,velZ =computeVelocity(loc_X,loc_Y,loc_Z)
    theta = computeTheta(velX,velY,velZ)

    thresholdDegree = 0.5 # upto x degree deviation  motion considered linear

    flag = 1# 1 for display plots 

    linearmotTimeStamp,jitterLoc  =eval(loc_X,loc_Y,loc_Z,theta,T,thresholdDegree,flag)


    #dump results
    linearmotion = "motResult.json"
    jitterLocFile = "jitterResult.json"

    with open(linearmotion, 'w') as f1:
        json.dump(linearmotTimeStamp, f1)

    with open(jitterLocFile, 'w') as f2:
        json.dump(jitterLoc, f2)



if __name__ == "__main__":
    # Call the main function
    main()

