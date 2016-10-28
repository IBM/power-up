# Kickstart for RHEL7

install
url --url=http://$http_server/$distro/

text

keyboard --vckeymap=us --xlayouts='us'
lang en_US.UTF-8
timezone America/Chicago

auth --enableshadow --enablemd5
user --name=defaultuser --groups=wheel --password=passw0rd
rootpw passw0rd

clearpart --all --initlabel
ignoredisk --only-use=$getVar('install_disk', '/dev/sda')
bootloader --location=mbr --boot-drive=$getVar('install_disk', '/dev/sda')
autopart

reboot

%packages
@core
bridge-utils
vim
wget
%end

%pre
$SNIPPET('kickstart_start')
%end

%post
# Add yum sources
# Add ssh keys to root
mkdir /root/.ssh
/bin/wget http://$http_server/authorized_keys -O /root/.ssh/authorized_keys
# Add ssh keys to defaultuser
mkdir /home/defaultuser/.ssh
/bin/wget http://$http_server/authorized_keys -O /home/defaultuser/.ssh/authorized_keys
/bin/chown defaultuser:defaultuser /home/defaultuser/.ssh/authorized_keys
# Enable passwordless sudo for defaultuser
echo -e "defaultuser\tALL=NOPASSWD: ALL" > /etc/sudoers.d/defaultuser
echo -e "[$distro]" > /etc/yum.repos.d/$(distro).repo
echo -e "name=$distro" >> /etc/yum.repos.d/$(distro).repo
echo -e "baseurl=http://$http_server/$distro/" >> /etc/yum.repos.d/$(distro).repo
echo -e "enabled=1" >> /etc/yum.repos.d/$(distro).repo
echo -e "gpgcheck=0" >> /etc/yum.repos.d/$(distro).repo
$SNIPPET('kickstart_done')
%end
