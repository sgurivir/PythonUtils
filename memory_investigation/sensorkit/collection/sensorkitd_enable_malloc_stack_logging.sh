mount -uw /

plutil -convert xml1 /System/Library/LaunchDaemons/com.apple.locationd.plist

sysctl -w kern.memorystatus_highwater_enabled=0
jetsam_properties set Daemon Override com.apple.locationd InactiveHardMemoryLimit -1
jetsam_properties set Daemon Override com.apple.locationd ActiveSoftMemoryLimit -1

defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist  EnvironmentVariables -dict MallocStackLogging lite
#defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist EnvironmentVariables -dict MallocStackLogging 1
launchctl unload /System/Library/LaunchDaemons/com.apple.locationd.plist
launchctl load /System/Library/LaunchDaemons/com.apple.locationd.plist

read -p "Needs Reboot. Press Enter to continue"
reboot

