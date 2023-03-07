基于Negamax、AlphaBeta剪枝等算法实现的简易国际象棋AI，可在命令行下与AI对局，或使用lichess作为前端界面。  
水平大概能达到lichess1700-2000分。  
**注意：** 残局库相关没有经过完备测试，如出现问题将相应代码删除即可，不影响主体功能。

#### 参考网站
* https://www.chessprogramming.org/Main_Page
* https://www.xqbase.com/computer.htm
* https://lichess.org/  

### 程序运行环境

-   **Python 3.10**
-   **相关库：**

    ![](https://s2.loli.net/2023/03/06/CfHrZwSoX8AlJIY.png)

    **pip install python-chess/conda install python-chess**

    **import chess**

-   **环境配置**

    **UI界面需要lichess的支持。**

-   将 repo 下载到 lichess-bot 目录中。
-   导航到 cmd/Terminal: 中的目录cd lichess-bot。
-   安装pip：apt install python3-pip.
-   安装虚拟环境：pip install virtualenv.
-   设置虚拟环境：apt install python3-venv。

    python3 -m venv venv \# If this fails you probably need to add Python3 to your PATH.

    virtualenv venv -p python3 \# If this fails you probably need to add Python3 to your PATH.

    source ./venv/bin/activate

    python3 -m pip install -r requirements.txt

-   复制config.yml.default到config.yml.

详情参照https://github.com/ShailChoksi/lichess-bot

### 程序运行结果展示

**1.通过控制台**

1.  初始页面，选择黑棋或者白棋

**![C:\\Users\\Lenovo\\AppData\\Local\\Temp\\1653747336(1).png](https://s2.loli.net/2023/03/06/coWTPiLVQnvwl3z.png)**

2.  输入操作进行棋子的移动

    ![](https://s2.loli.net/2023/03/06/a73pcNrUg2Oln6z.png)

3.  中间步骤

    ![](https://s2.loli.net/2023/03/06/7t8nvzeTUENgAbX.png)

4.  结束

    ![](https://s2.loli.net/2023/03/06/N8AKWhPDB7Ye6IL.png)

**2.连接lichess**

Cmd输入如下命令以激活lichess。

![](https://s2.loli.net/2023/03/06/Q9qHwXrmiJogSVI.png)

激活lichess

![](https://s2.loli.net/2023/03/06/sLe3D2mCVNOvtaQ.png)

lichessUI界面