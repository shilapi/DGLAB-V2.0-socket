# DGLAB-V2.0-socket

![GitHub last commit](https://img.shields.io/github/last-commit/shilapi/DGLAB-V2.0-socket)
![GitHub Release](https://img.shields.io/github/v/release/shilapi/DGLAB-V2.0-socket)
[![CodeFactor](https://www.codefactor.io/repository/github/shilapi/dglab-v2.0-socket/badge)](https://www.codefactor.io/repository/github/shilapi/dglab-v2.0-socket)

 一个完整的 DGLAB2.0 郊狼2.0 WebSocket 受控端实现。基于 [DGLAB-python-driver](https://github.com/shilapi/DGLAB-python-driver)。

 本项目的目标是让郊狼 2.0 主机也能用上 WebSocket 远控协议，降低玩家们的装备购置成本。

## 基础用法

 **修改**`config.yaml`：

|Key|Value|
|---|---|
|QR_Content|（可空）连接界面的二维码内容，为一串包含 ws:// 或 wss:// 的网址|
|Channel_A_limit|通道 A 强度上限|
|Channel_B_limit|通道 B 强度上限|
|Wave_convert_ratio|由 3.0 的波形转换到 2.0 波形的转换比例，具体请看下文转换比例一栏|
|Debug|是否开启 debug 模式|

若 `QR_Content` 留空，则会自动识别屏幕上的二维码。

 **安装依赖**

 ```
 pip3 install -r requirements
 ```

 **运行程式**

对于 Windows 用户，双击 `run.bat` 即可。

对于 Linux 用户，在 **`src` 的父目录** 执行如下指令：

```
python3 ./src/main.py
```

## 转换比例解释

由于郊狼 2.0 与 3.0 的波形存储方式不同，2.0 中由波形数据直接决定的对体感十分重要的波形频率被独立出来为一个单独的数值了。在官方的实现中，这一数值由被控者本人在 app 中自己设定，而 WS 协议并不会交换这一数值，因此我们需要预先设定一个转换比例。

简单来说，这一数值决定了你每次的电击体感是否强烈，这一数值应该介于 2-20 之间。**数值越小感觉越强烈。** 如若超出这一范围可能会导致体感过弱。
