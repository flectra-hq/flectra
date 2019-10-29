#!/bin/bash
if [ -f /etc/flectra/ssh-pwd ]; then
    echo "Root password already saved. Using this one"
    PASS=$(</etc/flectra/ssh-pwd)
else
    PASS=${ROOT_PASS:-$(pwgen -s 12 1)}
    _word=$( [ ${ROOT_PASS} ] && echo "preset" || echo "random" )
    echo "=> Setting a ${_word} password to the root user"
fi

echo "root:$PASS" | chpasswd
echo "flectra:$PASS" | chpasswd
echo "=> Done!"
echo $PASS > /etc/flectra/ssh-pwd
IP=$(hostname --ip-address)
echo "========================================================================"
echo "     You can now connect to this Developer Container via SSH using:"
echo ""
echo "                      ssh -p <port> root@${IP}"
echo "                              or"
echo "                      ssh -p <port> flectra@${IP}"
echo ""
echo "            and enter the password '$PASS' when prompted"
echo ""
echo "========================================================================"