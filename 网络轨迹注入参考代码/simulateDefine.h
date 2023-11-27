#ifndef SIMULATEDEFINE_H
#define SIMULATEDEFINE_H
#include <QVector>
#include <climits>
struct StartCommand
{
    long long commandWord;              //命令字,非触发启动0x0ABB9011
    long long startTime;                //仿真起始时间,自2006年1月1日零时以来的毫秒数
    long long simulateTime;             //仿真时长
    long long reserveLL1;               //预留
    double userLocationX;               //初始用户位置X
    double userLocationY;               //初始用户位置Y
    double userLocationZ;               //初始用户位置Z
    double reserverD1[9];               //预留
    long long reserveLL2[3];            //预留
    double roll;                        //初始载体横滚角
    double yaw;                         //初始载体方位角
    double pitch;                       //初始载体俯仰角
    double reserverD2[9];               //预留
};

/**
 * @brief 停止指令
 */
struct StopCommand
{
    unsigned int commandHead = 0x7B7B7B7B;  //指令头
    unsigned int commandLen;                //指令长度,从命令字开始的数据长度（16）（不验证，可为任意值）
    unsigned int commandWord = 0x9099;      //命令字
    unsigned int reserve = 0;               //预留
    unsigned int commandPram[58];           //指令参数,预留
};

/**
 * @brief 轨迹数据命令
 */
struct trajectoryDataCommand
{
    long long commandWord = 0x0A5A5C39;         //命令字
    long long trajectoryTime;                   //轨迹时间
    long long trajectoryNum;                    //轨迹序号
    long long traTimeProportionFactor;          //轨迹时间比例因子
    double userLocationX;                       //用户位置X
    double userLocationY;                       //用户位置Y
    double userLocationZ;                       //用户位置Z
    double userSpeedX;                          //用户速度X
    double userSpeedY;                          //用户速度Y
    double userSpeedZ;                          //用户速度Z
    double userAccelerationX;                   //用户加速度X
    double userAccelerationY;                   //用户加速度Y
    double userAccelerationZ;                   //用户加速度Z
    double userJerkX;                           //用户加加速度X
    double userJerkY;                           //用户加加速度Y
    double userJerkZ;                           //用户加加速度Z
    long long attitudeTime;                     //姿态时间
    long long attitudeNum;                      //姿态数据序号
    long long attTimeProportionFactor;          //姿态时间比例因子
    double carrierRoll;                         //载体横滚角
    double carrierYaw;                          //载体方位角
    double carrierPitch;                        //载体俯仰角
    double carrierRollAngularSpeedX;            //载体角速度X
    double carrierRollAngularSpeedY;            //载体角速度Y
    double carrierRollAngularSpeedZ;            //载体角速度Z
    double carrierRollAngularAccelerationX;     //载体角加速度X
    double carrierRollAngularAccelerationY;     //载体角加速度Y
    double carrierRollAngularAccelerationZ;     //载体角加速度Z
    double carrierAngularJerkX;                 //载体角加加速度X
    double carrierAngularJerkY;                 //载体角加加速度Y
    double carrierAngularJerkZ;                 //载体角加加速度Z

};

struct FileTrackData08
{
    double lCmd;
    double lTrackTimes; //仿真时间

    double dUserPosX;
    double dUserPosY;
    double dUserPosZ;

    double dUserVelX;
    double dUserVelY;
    double dUserVelZ;

    double dUserAccX;
    double dUserAccY;
    double dUserAccZ;

    double dUserJekX;
    double dUserJekY;
    double dUserJekZ;

    double dUserAzimu;
    double dUserPitch;
    double dUserRoll;

    double dUserAzimuVel;
    double dUserPitchVel;
    double dUserRollVel;

    //    double dUserAzimuAcc;
    //    double dUserPitchAcc;
    //    double dUserRollAcc;

    //    double dUserAzimuJek;
    //    double dUserPitchJek;
    //    double dUserRollJek;

};

struct simulate08
{
    simulate08()
    {
        userID = userCount++;
    }

    ~simulate08()
    {
        if (userCount != 0)
            userCount--;
    }

    void append(const struct trajectoryDataCommand &trj)
    {
        trjData.append(trj);
        total++;
    }

    bool checkMin()
    {
        if (total < min && total != 0)
        {
            min = total;
            return true;
        }
        return false;
    }

    int userID = 0;                      /**< 用户ID */
    int total = 0;                       /**< 轨迹总数 */
    int current = 0;                     /**< 当前计数 */
    QVector<struct trajectoryDataCommand> trjData;         /**< 轨迹数据 */

public:
    static int min;                      /**< 最少轨迹总数,避免多用户时访问越界 */

private:
    static int userCount;                /**< 用户计数 */
};


#endif // SIMULATEDEFINE_H
