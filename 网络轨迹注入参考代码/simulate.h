#ifndef SIMULATE_H
#define SIMULATE_H
#include "simulateDefine.h"
#include "../InjectorInterface.h"
#include "MainDefine.h"
#include "Utils/ComUdpDirect.h"
#include <QFile>
#include "../Utils/Utils.h"
#include <QFileDialog>
class simulate :public InjectorInterface
{
public:
    simulate();
    ~simulate();
    void startCommand();
    void stopCommand();
    void configCommand();

    void sendConfig() override;

    int startSim() override;

    int stopSim() override;

    int showSpecified()  override;

    const QString about() override;

    int startSend(int interVal) override;

    int stopSend() override;

    int userNum()  override;

    Endian endian() override;

    int readFile(int row, int trjType, const QString &fileName) override;

    int releaseTrjData(int row) override;
    struct StartCommand StartCommand;
    struct StopCommand StopCommand;
    struct trajectoryDataCommand trajectoryDataCommand;
    bool ContainNetHead = true;
    int m_userNum = 3;
public slots:
    int sendNextFrame() override;
private:
    simulate08 *m_buffer[3];
//    struct trajectoryDataCommand *m_trjdata[3];
    unsigned int  totalCounts[3];
    unsigned m_trjCount;
};

#endif // SIMULATE_H
