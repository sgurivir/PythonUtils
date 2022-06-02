mount -uw /

plutil -convert xml1 /System/Library/LaunchDaemons/com.apple.locationd.plist

sysctl -w kern.memorystatus_highwater_enabled=0
jetsam_properties set Daemon Override com.apple.locationd InactiveHardMemoryLimit -1
jetsam_properties set Daemon Override com.apple.locationd ActiveSoftMemoryLimit -1

read -p "Needs Reboot. Press Enter to continue"
reboot

