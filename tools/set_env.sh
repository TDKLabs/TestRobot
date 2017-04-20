#!/bin/sh

# export TOOLCHAIN
export TOOLCHAIN=/opt/tdk
export TROBOT=$TOOLCHAIN

# set PATH
export PATH=/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin

# export TDK libs path
export PATH=$TOOLCHAIN/libs/apache-ant-1.8.4/bin:$TOOLCHAIN/libs/apache-maven-3.2.5/bin:$TOOLCHAIN/libs/SoapUI-5.2.0/bin:$TOOLCHAIN/libs/groovy-2.2.2/bin:$PATH

# export tools and interpreters path
export PATH=$TOOLCHAIN/tools:$PATH

# export PYTHONLIB path
export PYTHONPATH=$TOOLCHAIN/libs/tdklabs

# export JAVA_HOME
#export JAVA_HOME=/opt/java/latest

# export GECKO_DRIVER
export PATH=$TOOLCHAIN/lin:$PATH

# export FF_HOME
export FF_HOME=/home/demo/firefox/firefox-45.5.0esr
export PATH=$FF_HOME:$PATH
export LD_LIBRARY_PATH=$FF_HOME:$LD_LIBRARY_PATH

export GROOVY_HOME=$TOOLCHAIN/libs/groovy-2.2.2

echo PATH:$PATH

. /home/demo/node/bin/activate
