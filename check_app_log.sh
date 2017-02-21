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
_key="ERROR\|Exception\|OutOfMemoryError\|SocketException"
_ignore="INFO|Reference|DEBUG|There is no Action mapped for namespace"

modlog=`echo $rtn | awk -F'|' '{print $2}'`
###########################################################################
if [ ! -f $modlog ];then
        echo "ERROR     Check Log $modlog doesn't exsit..."
        exit 1;

fi


##########################################################################
#tail -n100000 $modlog | egrep "$_date1|$_date2|$_date3|$_now_date" | egrep -Ev "$_ignore" | egrep -wi "$_key" > /t                                                                                                                          mp/.$modname.log
### Variable flag to change status of service, then check log on evenlog####
mod_flag=/tmp/$modname.flag
if [ ! -f $mod_flag ]
then
  touch $mod_flag
  echo "True" > $mod_flag
fi
tail -n10000 $modlog  | egrep -Ev "$_ignore" > /tmp/$modname.log

mod_warn=/tmp/$modname.warn
mod_error=/tmp/$modname.error

if [ ! -f $mod_warn ]
then
  touch $mod_warn
fi

if [ ! -f $mod_error ]
then
  touch $mod_error
fi

cat /tmp/$modname.log |grep -wi " WARN " >> $mod_warn
cat /tmp/$modname.log |grep -Ev " WARN "|grep -wi "$_key" >> $mod_error


_size_error=`ls -l $mod_error | awk '{print $5}'`
_size_warn=`ls -l $mod_warn | awk '{print $5}'`
_flag=`cat $mod_flag`
if [[ $_size_error -lt 1 && $_size_warn -lt 1 ]];then
   echo  "$modname.log Normal...."
   exit 0
else
   if [ $_size_error -gt 0 ];then
      if [ "$_flag" == "True" ];then
         echo "False" > $mod_flag
             _lineerror=`head -n 1 $mod_error`
             sed -i '1d' /tmp/$modname.error
             echo $_lineerror
             exit 2
      else
         echo "True" > $mod_flag
         echo "Change Status Service"
         exit 0
      fi
   else
      if [ "$_flag" == "True" ];then
         echo "False" > $mod_flag
         _linewarn=`head -n 1 $mod_warn`
         sed -i '1d' /tmp/$modname.warn
         echo $_linewarn
         exit 1
      else
         echo "True" > $mod_flag
         echo "Change Status Service"
         exit 0
      fi
   fi
fi
