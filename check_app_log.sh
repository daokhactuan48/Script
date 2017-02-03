#!/bin/bash
_mod_list="SC_TOMCAT_FRONT1|/opt/trs_be.log
DL_TOMCAT|/opt/dl_tomcat.log"

##############################################################################
usage(){
   echo "Usage: $0 < modelname >"
   echo ""
   echo "which model log do you want to check:"
   echo ""
   for mod in `echo $_mod_list | sed 's/ /\n/g' | grep -v "^#" `;do
      echo $mod | awk -F'|' '{printf("%-16s\t%s\n",$1,$2);}'
   done
   echo ""
   exit 1
}

#############################################################################
if [ $# -ne 1 ]; then
   usage
else
   rtn=`echo $_mod_list | sed 's/ /\n/g' | grep -v "^#" | grep "^$1"`
   modname=`echo $rtn | awk -F'|' '{print $1}'`

   if [ "$1" != "$modname" ];then
      usage
   fi
fi

##########################################################################


############################################################################
_now_date=`date "+%Y-%m-%d %H:%M"`
_date1=`date -d"1 min ago" +"%Y-%m-%d %H:%M"`
_date2=`date -d"2 min ago" +"%Y-%m-%d %H:%M"`
_date3=`date -d"3 min ago" +"%Y-%m-%d %H:%M"`
_key="ERROR|Exception|OutOfMemoryError|SocketException"
_ignore="INFO|Reference|DEBUG|There is no Action mapped for namespace"

modlog=`echo $rtn | awk -F'|' '{print $2}'`
###########################################################################
if [ ! -f $modlog ];then
        echo "ERROR     Check Log $modlog doesn't exsit..."
        exit 1;

fi
####################################
#Process=`echo $modname | sed 's/[0-9]*//g'`
#ps uxa | grep $Process | grep -v "grep\|check_app_log" > /dev/null
#if [ $? -ne 0  ]; then
#        echo "$Process is not running !!!!! Change your configure."
#        exit 1

#fi

##########################################################################
#tail -n100000 $modlog | egrep "$_date1|$_date2|$_date3|$_now_date" | egrep -Ev "$_ignore" | egrep -wi "$_key" > /tmp/.$modname.log
### Variable flag to change status of service, then check log on evenlog####
mod_flag=/tmp/.$modname.flag
if [ ! -f $mod_flag ]
then
  touch $mod_flag
  echo "True" > $mod_flag
fi
tail -n10000 $modlog  | egrep -Ev "$_ignore" | egrep -wi "$_key" >> /tmp/.$modname.log 
##File modname.error.log store error delete####
mod_error_log=/tmp/.$modname.error.log
if [ ! -f $mod_error_log ]
then
  touch $mod_error_log
fi
_size=`ls -l /tmp/.$modname.log | awk '{print $5}'`
_flag=`cat $mod_flag`
if [ $_size -lt 1 ];then
   echo  "$modname.log Normal...."
   exit 0
else
   if [ "$_flag" == "True" ];then
         echo "False" > $mod_flag
  	 _lineerror=`head -n 1 /tmp/.$modname.log`
   	 sed -i '1d' /tmp/.$modname.log
  	 echo $_lineerror >> $mod_error_log
         echo $_lineerror
  	 exit 2
   else
        echo "True" > $mod_flag
        echo "Change Status Service"
        exit 0
   fi
fi

