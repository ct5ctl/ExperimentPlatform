#include "simulate.h"
#include "../DataHelper.h"
#include <string.h>


int simulate08::userCount = 0;
int simulate08::min = INT_MAX;

simulate::simulate()
{
    m_name = "后台网络注入";
    m_trjCount = 0;
}
simulate::~simulate()
{
    m_trjCount = 0;
}

void simulate::startCommand()
{


}
void simulate::stopCommand()
{


}
void simulate::configCommand()
{


}
/**************以下为重写纯虚函数*****************/
void simulate:: sendConfig()
{

}

int simulate::startSim()
{
    int userNum = DataHelper::instance()->userNum();
    QByteArray startMsg;
    for (int i = 0; i < userNum; ++i)
    {
        struct StartCommand userInfo {};
        memset(&userInfo, 0x00, sizeof(userInfo));
        userInfo.commandWord = 0x0ABB9011;
        userInfo.startTime = DataHelper::instance()->startTime();
        userInfo.simulateTime = 72000;
        userInfo.userLocationX = m_buffer[i]->trjData[0].userLocationX;
        userInfo.userLocationY = m_buffer[i]->trjData[0].userLocationY;
        userInfo.userLocationZ = m_buffer[i]->trjData[0].userLocationZ;
        userInfo.roll = m_buffer[i]->trjData[0].carrierRoll;
        userInfo.yaw = m_buffer[i]->trjData[0].carrierYaw;
        userInfo.pitch = m_buffer[i]->trjData[0].carrierPitch;

        startMsg.append(Utils::toByteArray(userInfo));
    }
    return    m_com->sendCommand(UdpMsgClass::MsgClassControl, ControlMsgNo::CtrlMsgStart,
                                 startMsg, ContainNetHead);

}

int simulate::stopSim()
{
    memset(&StopCommand, 0x00, sizeof(StopCommand));
    StopCommand.commandHead = 0x7B7B7B7B;
    StopCommand.commandWord = 0x9099;
    m_com->sendCommand(UdpMsgClass::MsgClassControl, ControlMsgNo::CtrlMsgStop,
                       Utils::toByteArray(StopCommand), ContainNetHead);
    return 0;
}

int simulate::showSpecified()
{

}

const QString simulate::about()
{

}

int simulate::startSend(int interVal)
{
    qDebug() << "发送时用户数为：" << DataHelper::instance()->userNum();
    connect(&m_timer, &QTimer::timeout, this, &simulate::sendNextFrame);
    m_timer.start(interVal);

    return 0;

}
int simulate::stopSend()
{
    m_timer.stop();
    return 0;
}

int simulate::userNum()
{
    return m_userNum;
}

Endian simulate::endian()
{

}

int simulate::readFile(int row, int trjType, const QString &fileName)
{
    Q_UNUSED(trjType)
    QFile trjFile(fileName);
    QStringList m_strList;
    trjFile.open(QIODevice::ReadOnly);
    QTextStream data(&trjFile);
    if (!trjFile.isOpen())
    {
        qWarning() << "打开轨迹文件失败，请检查文件是否存在！";
    }
    else
    {

        releaseTrjData(row);
        m_strList.clear();

        while (!data.atEnd())
        {
            QString str = data.readLine();
            m_strList.append(str);
        }
        if (m_buffer[row] != nullptr)
        {
            delete m_buffer[row];
            m_buffer[row] = nullptr;
        }
        m_buffer[row] = new simulate08;
        totalCounts[row] = 0;
        for (qint32 j = 0; j < m_strList.size(); j++)
        {
            QString str = m_strList.at(j);
            QStringList line = str.split(" ");
            if (line.size() < 20)
                continue;
            struct trajectoryDataCommand trjLine {};
            trjLine.trajectoryTime              = (long long)(line.at(1).toDouble() * 1000 + 1e-6);
            trjLine.trajectoryNum               = j;
            trjLine.userLocationX               = line.at(2).toDouble();
            trjLine.userLocationY               = line.at(3).toDouble();
            trjLine.userLocationZ               = line.at(4).toDouble();

            trjLine.userSpeedX                  = line.at(5).toDouble();
            trjLine.userSpeedY                  = line.at(6).toDouble();
            trjLine.userSpeedZ                  = line.at(7).toDouble();
            trjLine.userAccelerationX           = line.at(8).toDouble();
            trjLine.userAccelerationY           = line.at(9).toDouble();
            trjLine.userAccelerationZ           = line.at(10).toDouble();

            trjLine.userJerkX                   = line.at(11).toDouble();
            trjLine.userJerkX                   = line.at(12).toDouble();
            trjLine.userJerkX                   = line.at(13).toDouble();

            trjLine.carrierRoll                 = line.at(14).toDouble();
            trjLine.carrierPitch                = line.at(15).toDouble();
            trjLine.carrierYaw                  = line.at(16).toDouble();

            m_buffer[row]->append(trjLine);
            totalCounts[row]                    = j;
        }
        m_buffer[row]->checkMin();
        return m_buffer[row]->total;
    }
    return 0;
}

int simulate::releaseTrjData(int row)
{
    m_trjCount = 0;
    //    m_trjdata[row] = nullptr;
    //m_trj5091 = nullptr;
    return 0;
}

int simulate::sendNextFrame()
{
    QByteArray data;
    for (int i = 0; i < DataHelper::instance()->userNum(); ++i)
    {
        if (m_trjCount >= totalCounts[i])
        {
            qDebug() << "轨迹数据已发送完成，复位数据索引" << m_trjCount << "totalCounts[i]" << totalCounts[i];
            m_timer.stop();
            m_trjCount = 0;
            return -1;
        }
        data.append(reinterpret_cast<char *>(&m_buffer[i]->trjData[m_trjCount]), sizeof(trajectoryDataCommand));
        qDebug() << m_buffer[i]->trjData[m_trjCount].trajectoryTime;

    }

    m_com->sendCommand(UdpMsgClass::MsgClassControl, ControlMsgNo::CtrlMsgStart,
                       data, ContainNetHead);
    m_trjCount++;
    return 0;
}
